from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.articles.models import Article, ArticleMetadata
from retrievers.base import Document
from retrievers.intent_classifier import Intent, IntentResult

from .models import Conversation, Message

User = get_user_model()


def make_rag_response(answer="The answer.", used_fallback=False, documents=None):
    if documents is None:
        documents = [Document("Doc Title", "Wikipedia", "https://en.wikipedia.org/wiki/X", "content", 0.9, "wikipedia")]
    result = MagicMock()
    result.answer = answer
    result.intent = IntentResult(Intent.DEFINITION, "subject", "definition wording")
    result.documents = documents
    result.used_fallback = used_fallback
    return result


class ChatTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pass12345")
        self.article = Article.objects.create(
            category="technology", title="Chat Article", url="https://example.com/chat-article",
            content="Some content", summary="Summary",
        )
        ArticleMetadata.objects.create(article=self.article, verification_status="VERIFIED", source_trust=1,
                                       quality_score=1, freshness_score=1, evidence={"corroborating_sources": []})
        self.client.force_authenticate(user=self.user)

    def test_unauthorized_chat_rejected(self):
        self.client.force_authenticate(user=None)
        resp = self.client.post("/api/chat/", {"question": "What is this?", "article_id": self.article.id}, format="json")
        self.assertEqual(resp.status_code, 401)

    def test_missing_article_and_conversation_id_is_bad_request(self):
        resp = self.client.post("/api/chat/", {"question": "Hi"}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_invalid_article_id_is_404(self):
        resp = self.client.post("/api/chat/", {"question": "Hi", "article_id": 999999}, format="json")
        self.assertEqual(resp.status_code, 404)

    @patch("apps.chat.services.RAGService")
    def test_chat_happy_path_creates_conversation_and_messages(self, mock_rag_cls):
        mock_rag_cls.return_value.answer_question.return_value = make_rag_response()

        resp = self.client.post("/api/chat/", {"question": "What is X?", "article_id": self.article.id}, format="json")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["answer"], "The answer.")
        self.assertEqual(resp.data["trust_status"], "grounded")
        self.assertEqual(len(resp.data["citations"]), 1)
        self.assertEqual(resp.data["metadata"]["intent"], "DEFINITION")

        conversation_id = resp.data["conversation_id"]
        self.assertEqual(Conversation.objects.filter(id=conversation_id, user=self.user).count(), 1)
        self.assertEqual(Message.objects.filter(conversation_id=conversation_id).count(), 2)

    @patch("apps.chat.services.RAGService")
    def test_chat_continues_existing_conversation(self, mock_rag_cls):
        mock_rag_cls.return_value.answer_question.return_value = make_rag_response()

        first = self.client.post("/api/chat/", {"question": "First?", "article_id": self.article.id}, format="json")
        conversation_id = first.data["conversation_id"]

        second = self.client.post("/api/chat/", {"question": "Follow up?", "conversation_id": conversation_id}, format="json")

        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.data["conversation_id"], conversation_id)
        self.assertEqual(Message.objects.filter(conversation_id=conversation_id).count(), 4)

    def test_conversation_owned_by_other_user_is_404_not_403(self):
        other = User.objects.create_user(username="mallory", password="pass12345")
        conversation = Conversation.objects.create(user=other, article=self.article)

        resp = self.client.get(f"/api/chat/{conversation.id}/")
        self.assertEqual(resp.status_code, 404)

    def test_invalid_conversation_id_is_404(self):
        resp = self.client.get("/api/chat/999999/")
        self.assertEqual(resp.status_code, 404)

    @patch("apps.chat.services.RAGService")
    def test_retrieval_failure_falls_back_gracefully_not_500(self, mock_rag_cls):
        mock_rag_cls.return_value.answer_question.side_effect = RuntimeError("retriever exploded")

        resp = self.client.post("/api/chat/", {"question": "Boom?", "article_id": self.article.id}, format="json")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["trust_status"], "fallback")
        self.assertTrue(resp.data["answer"])

    @patch("apps.chat.services.RAGService")
    def test_history_lists_only_own_conversations(self, mock_rag_cls):
        mock_rag_cls.return_value.answer_question.return_value = make_rag_response()
        self.client.post("/api/chat/", {"question": "Hi", "article_id": self.article.id}, format="json")

        other = User.objects.create_user(username="carol", password="pass12345")
        Conversation.objects.create(user=other, article=self.article)

        resp = self.client.get("/api/history/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_unauthorized_history_rejected(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get("/api/history/")
        self.assertEqual(resp.status_code, 401)
