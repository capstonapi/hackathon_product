"""Concrete retrievers. Each one returns the shared Document type. Ported from capston_end/retrievers."""
import html
import logging
import re

from apps.articles.services import find_similar_by_embedding
from apps.search.services import search_entities
from services.embedder import generate_embedding
from services.web_search import search_google_news, search_web, search_wikipedia

from .base import BaseRetriever, Document, RetrievalRequest
from .source_policy import source_metadata

logger = logging.getLogger(__name__)


class ArticleRetriever(BaseRetriever):
    def retrieve(self, request):
        article = request.article or {}
        content = (article.get("content") or article.get("summary") or "").strip()
        return [Document(article.get("title") or "Current article", article.get("source") or "Current article", article.get("url") or "", content[:4000], 1.0, "current_article")] if content else []


class VectorRetriever(BaseRetriever):
    def retrieve(self, request):
        embedding = generate_embedding(request.question)
        if not embedding:
            return []
        try:
            article = request.article or {}
            rows = find_similar_by_embedding(embedding, exclude_article_id=article.get("id"), limit=5)
        except Exception as error:
            logger.warning("Vector retrieval failed: %s", error)
            return []
        return [
            Document(
                row.title or "Untitled article",
                row.source or "Article archive",
                row.url or "",
                (row.summary or row.content or "")[:1200],
                max(0.0, 1 - float(row.distance or 0)),
                "vector_db",
            )
            for row in rows
        ]


class GraphRetriever(BaseRetriever):
    """Entity/event graph traversal over controlled article relationships.

    The article/entity store is the graph: Article -> mentions -> Entity and
    article context links are related events. It is deliberately only used for
    historical relationship questions, never simple definitions.
    """
    def retrieve(self, request):
        subject = (request.subject or "").strip()
        if len(subject) < 2:
            return []
        try:
            rows = search_entities(subject, limit=5)
        except Exception as error:
            logger.warning("Graph entity traversal failed: %s", error)
            return []
        return [Document(row.title, row.source or "Article archive", row.url, (row.summary or row.content or "")[:1200], .82 - index * .04, "entity_graph", row.published_at or "", trust_score=.65) for index, row in enumerate(rows)]


class ExternalNewsRetriever(BaseRetriever):
    def retrieve(self, request):
        return [self._document(row, .75 - index * .03) for index, row in enumerate(search_google_news(request.question, max_results=3))]

    @staticmethod
    def _document(row, relevance):
        meta = source_metadata(row.get("source") or "Google News", row.get("url") or "")
        return Document(row.get("title") or "Untitled news result", row.get("source") or "Google News", row.get("url") or "", (row.get("summary") or "")[:1000], relevance, meta["source_type"], row.get("published_at") or "", trust_score=meta["trust_score"])


class WikipediaRetriever(BaseRetriever):
    def retrieve(self, request):
        rows = search_wikipedia(request.subject or request.question, max_results=2)
        return [Document(row.get("title") or request.subject, "Wikipedia", row.get("url") or "", html.unescape(re.sub(r"<[^>]+>", "", row.get("summary") or "")), .98 - index * .02, "reference", trust_score=.78) for index, row in enumerate(rows)]


class OfficialWebsiteRetriever(BaseRetriever):
    def retrieve(self, request):
        subject = request.subject or request.question
        return self._search(f"{subject} official website", "official_website")

    @staticmethod
    def _search(query, source_type):
        docs = []
        for index, row in enumerate(search_web(query, max_results=4)):
            title, url = row.get("title") or "Official source", row.get("url") or ""
            meta = source_metadata(row.get("source") or "", url)
            if meta["source_type"] == "official":
                docs.append(Document(title, row.get("source") or "Official source", url, (row.get("summary") or "")[:1000], .96 - index * .02, source_type, trust_score=meta["trust_score"]))
        return docs[:2]


class OfficialBiographyRetriever(OfficialWebsiteRetriever):
    def retrieve(self, request):
        return self._search(f"{request.subject or request.question} official biography", "official_biography")
