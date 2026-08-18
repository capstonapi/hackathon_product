"""
Chat orchestration: resolves/creates a Conversation, calls the ported
RAGService, persists both turns, and shapes the response so the API never
leaks prompts or chain-of-thought -- only the final answer, its citations,
and a trust signal.
"""
import logging
import time

from django.utils import timezone

from django.shortcuts import get_object_or_404

from apps.articles.services import get_article
from retrievers.rag_service import RAGService

from .models import Conversation, Message

logger = logging.getLogger("news_agent.chat")


def _article_to_dict(article):
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "summary": article.summary,
        "source": article.source,
        "url": article.url,
    }


def _resolve_conversation(user, article_id, conversation_id):
    if conversation_id is not None:
        return get_object_or_404(Conversation, pk=conversation_id, user=user)
    article = get_article(article_id)
    return Conversation.objects.create(user=user, article=article)


def _trust_status(used_fallback, documents):
    if used_fallback:
        return "fallback"
    if not documents:
        return "low_confidence"
    return "grounded"


def _memory_for(conversation):
    """Bounded scoped memory; never forward an unlimited conversation to the model."""
    recent = list(conversation.messages.order_by("-created_at")[:6])
    recent.reverse()
    turns = "\n".join(f"{m.role}: {m.content[:500]}" for m in recent)
    return f"Article: {conversation.article.title}\nRecent turns:\n{turns}"[:4000]


def ask_question(user, question, article_id=None, conversation_id=None):
    started = time.monotonic()
    conversation = _resolve_conversation(user, article_id, conversation_id)
    Message.objects.create(conversation=conversation, role="user", content=question)

    article_dict = _article_to_dict(conversation.article)

    try:
        result = RAGService().answer_question(question, article_dict, memory=_memory_for(conversation))
        answer, intent, documents, used_fallback = result.answer, result.intent, result.documents, result.used_fallback
    except Exception:
        logger.exception("RAG pipeline failed for conversation_id=%s", conversation.id)
        answer = "We couldn't retrieve extra context for this question right now. Please try again shortly."
        intent, documents, used_fallback = None, [], True

    trust_status = _trust_status(used_fallback, documents)
    citations = [
        {"marker": i, "source": doc.source, "title": doc.title, "url": doc.url, "published_at": doc.published_at or None, "retrieved_at": doc.retrieved_at or None}
        for i, doc in enumerate(documents, 1)
    ]
    sources = [
        {
            "source_type": doc.source_type,
            "source": doc.source,
            "title": doc.title,
            "url": doc.url,
            "relevance_score": doc.relevance_score,
            "published_at": doc.published_at or None,
            "retrieved_at": doc.retrieved_at or None,
            "trust_score": doc.trust_score,
        }
        for doc in documents
    ]

    retrieval_plan = [type(doc).__name__ for doc in documents]
    metadata = {"intent": intent.intent.value if intent else None, "retrieval_plan": retrieval_plan, "model": "gemini", "timestamp": timezone.now().isoformat(), "source_count": len(documents)}
    Message.objects.create(
        conversation=conversation, role="assistant", content=answer,
        citations=citations, sources=sources, trust_status=trust_status,
    )
    conversation.save()  # bump updated_at

    logger.info(
        "chat answered conversation_id=%s intent=%s trust_status=%s sources=%d latency_ms=%d",
        conversation.id, intent.intent.value if intent else None, trust_status, len(documents), int((time.monotonic() - started) * 1000),
    )

    return {
        "conversation_id": conversation.id,
        "answer": answer,
        "citations": citations,
        "sources": sources,
        "trust_status": trust_status,
        "metadata": metadata,
    }


def get_conversation_messages(user, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id, user=user)
    return conversation.messages.all()


def list_conversations(user):
    return Conversation.objects.filter(user=user)
