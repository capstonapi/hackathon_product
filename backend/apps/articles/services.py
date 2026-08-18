"""
Controlled read/write functions for articles. This is the only path any
view, retriever, or agent-facing tool is allowed to use to reach the
`articles` table -- no raw SQL, no string-built queries.
"""
import logging

from django.db.models import Count
from django.shortcuts import get_object_or_404
from pgvector.django import CosineDistance

from .governance import verified_articles
from .models import Article, SavedArticle

logger = logging.getLogger("news_agent.articles")

# Ported from capston_end/config.py UI_CATEGORY_TO_GNEWS_CATEGORIES + app.py DISPLAY_CATEGORIES.
DISPLAY_CATEGORIES = [
    {"key": "politics", "title": "Politics", "source_categories": ["nation"]},
    {"key": "economy", "title": "Economy", "source_categories": ["business"]},
    {"key": "science-tech", "title": "Science and Technology", "source_categories": ["science", "technology"]},
    {"key": "sports", "title": "Sports", "source_categories": ["sports"]},
    {"key": "international", "title": "International", "source_categories": ["world"]},
]


def get_article(article_id):
    return get_object_or_404(verified_articles(), pk=article_id)


def resolve_category_filter(category):
    """
    `category` may be a raw GNews category (matches Article.category
    directly, e.g. "business") or a UI category key from
    get_categories_with_counts() (e.g. "economy", which covers ["business"]).
    Returns the list of raw categories to filter on, or None for "no filter".
    """
    if not category:
        return None
    for display_category in DISPLAY_CATEGORIES:
        if display_category["key"] == category:
            return display_category["source_categories"]
    return [category]


def list_articles(category=None, source=None, date_from=None, date_to=None):
    qs = verified_articles()
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


def latest_articles():
    return verified_articles().order_by("-fetched_at")


def get_categories_with_counts():
    counts = {row["category"]: row["n"] for row in verified_articles().values("category").annotate(n=Count("id"))}
    return [
        {
            "key": c["key"],
            "title": c["title"],
            "count": sum(counts.get(sc, 0) for sc in c["source_categories"]),
        }
        for c in DISPLAY_CATEGORIES
    ]


def find_similar_by_embedding(embedding, exclude_article_id=None, limit=5):
    """Nearest neighbors by cosine distance. Used both by /related/ and by the RAG VectorRetriever."""
    qs = verified_articles().filter(embedding__isnull=False)
    if exclude_article_id is not None:
        qs = qs.exclude(pk=exclude_article_id)
    return qs.annotate(distance=CosineDistance("embedding", embedding)).order_by("distance")[:limit]


def get_related(article_id, limit=5):
    article = get_article(article_id)
    if article.embedding is None:
        return Article.objects.none()
    return find_similar_by_embedding(article.embedding, exclude_article_id=article.id, limit=limit)


def get_timeline(article_id):
    """Chronological view built from the insight generator's stored context_article_ids."""
    article = get_article(article_id)
    context_ids = article.context_article_ids or []
    events = list(verified_articles().filter(id__in=context_ids)) + [article]
    events.sort(key=lambda a: a.published_at or "")
    return {
        "narrative": article.timeline,
        "events": [
            {"id": a.id, "title": a.title, "source": a.source, "published_at": a.published_at, "url": a.url}
            for a in events
        ],
    }


def save_article_for_user(user, article_id):
    article = get_article(article_id)
    SavedArticle.objects.get_or_create(user=user, article=article)


def unsave_article_for_user(user, article_id):
    SavedArticle.objects.filter(user=user, article_id=article_id).delete()


def list_saved_articles(user):
    return verified_articles().filter(saved_by__user=user).order_by("-saved_by__created_at")
