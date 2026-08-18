"""
Controlled search functions. Every lookup here is a fixed, parameterized
query written by us -- nothing here ever concatenates user input into SQL
text, and nothing here gives an LLM/agent a way to run arbitrary SQL.
"""
import logging

from django.db.models import FloatField, Q, Value
from pgvector.django import CosineDistance

from apps.articles.models import Article
from apps.articles.governance import verified_articles
from apps.articles.services import resolve_category_filter
from services.embedder import generate_embedding
from services.web_search import search_external_knowledge_base

logger = logging.getLogger("news_agent.search")


def _apply_common_filters(qs, category=None, source=None, date_from=None, date_to=None):
    categories = resolve_category_filter(category)
    if categories:
        qs = qs.filter(category__in=categories)
    if source:
        qs = qs.filter(source__icontains=source)
    if date_from:
        qs = qs.filter(fetched_at__gte=date_from)
    if date_to:
        qs = qs.filter(fetched_at__lte=date_to)
    return qs


def search_articles(query, mode="semantic", category=None, source=None, date_from=None, date_to=None, limit=20):
    """
    mode="semantic" (default): embed the query, rank by cosine distance.
    mode="keyword": case-insensitive title/summary match, newest first.
    Both accept the same category/source/date filters and annotate a
    `distance` attribute so callers/serializers have one uniform shape.
    """
    if mode == "keyword":
        qs = verified_articles().filter(Q(title__icontains=query) | Q(summary__icontains=query))
        qs = _apply_common_filters(qs, category, source, date_from, date_to)
        qs = qs.annotate(distance=Value(None, output_field=FloatField())).order_by("-fetched_at")
        return qs[:limit]

    embedding = generate_embedding(query)
    if embedding is None:
        # Search remains useful when the embedding provider is unavailable.
        # This is a controlled ORM query, not an LLM-generated query.
        logger.warning("semantic_search_fallback mode=keyword")
        qs = verified_articles().filter(Q(title__icontains=query) | Q(summary__icontains=query))
        qs = _apply_common_filters(qs, category, source, date_from, date_to)
        return qs.annotate(distance=Value(None, output_field=FloatField())).order_by("-fetched_at")[:limit]

    qs = verified_articles().filter(embedding__isnull=False)
    qs = _apply_common_filters(qs, category, source, date_from, date_to)
    return qs.annotate(distance=CosineDistance("embedding", embedding)).order_by("distance")[:limit]


def search_entities(query, limit=20):
    """Find articles whose extracted entities mention `query` (parameterized raw SQL, mapped to Article)."""
    sql = """
        SELECT DISTINCT a.*
        FROM articles a
        JOIN articles_articlemetadata m ON m.article_id = a.id
        CROSS JOIN LATERAL jsonb_array_elements(a.entities) e
        WHERE e->>'text' ILIKE %s
          AND m.verification_status = 'VERIFIED'
        ORDER BY a.fetched_at DESC
        LIMIT %s
    """
    return list(Article.objects.raw(sql, [f"%{query}%", limit]))


def search_external_sources(query, max_results_per_source=2):
    return search_external_knowledge_base(query, max_results_per_source=max_results_per_source)
