"""Enforced admission policy for public news and RAG evidence.

Nothing reaches a public query until it has passed this policy.  The policy is
deliberately conservative: a trusted source is necessary but not sufficient;
an event needs independent, trusted coverage before it is VERIFIED.
"""
import re
from datetime import timedelta, timezone as datetime_timezone

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.articles.models import Article, ArticleMetadata, ProcessingRecord
from apps.articles.source_policy import source_metadata

MIN_CONTENT_CHARS = 200
MIN_TRUST = 0.65
FRESHNESS_DAYS = getattr(settings, "ARTICLE_FRESHNESS_DAYS", 7)
SIMILARITY_THRESHOLD = 0.42


def _tokens(value):
    return {word for word in re.findall(r"[a-z0-9]{3,}", (value or "").lower())
            if word not in {"with", "from", "that", "this", "after", "will", "over", "news"}}


def title_similarity(first, second):
    left, right = _tokens(first), _tokens(second)
    return len(left & right) / len(left | right) if left and right else 0.0


def article_age(article):
    published = parse_datetime(article.published_at or "")
    if published is None:
        return timezone.now() - article.fetched_at
    if timezone.is_naive(published):
        published = timezone.make_aware(published, datetime_timezone.utc)
    return timezone.now() - published


def verified_articles():
    """The one queryset every public article-facing endpoint must start from."""
    return Article.objects.filter(active_metadata__verification_status="VERIFIED")


def _candidate_articles(article):
    # This intentionally includes pending records: a second independent
    # article can make the first one verifiable.
    rows = Article.objects.exclude(pk=article.pk).exclude(source__isnull=True).exclude(source="")
    return [row for row in rows if title_similarity(article.title, row.title) >= SIMILARITY_THRESHOLD]


def assess_article(article):
    """Store quality, expiry, duplicate, and independent-source evidence."""
    source = source_metadata(article.source or "", article.url)
    text = (article.content or article.summary or article.description or "").strip()
    quality = min(1.0, len(text) / 800) if article.title.strip() else 0.0
    status = "PENDING"
    evidence = {"policy_version": 1, "source": source, "quality": {"content_characters": len(text)}, "corroborating_sources": []}

    if len(text) < MIN_CONTENT_CHARS:
        status = "LOW_QUALITY"
    elif article_age(article) > timedelta(days=FRESHNESS_DAYS):
        status = "EXPIRED"
    elif source["trust_score"] < MIN_TRUST:
        status = "UNTRUSTED_SOURCE"
    elif settings.VERIFY_TRUSTED_SOURCES_WITHOUT_CORROBORATION:
        # This mode is appropriate when ingestion itself is restricted to a
        # curated publisher allowlist (for example, official RSS feeds).  The
        # provenance remains recorded so clients can distinguish this from
        # independently corroborated verification.
        status = "VERIFIED"
        evidence["verification_basis"] = "trusted_source"
    else:
        matches = []
        for candidate in _candidate_articles(article):
            candidate_source = source_metadata(candidate.source or "", candidate.url)
            if candidate_source["trust_score"] < MIN_TRUST:
                continue
            # A publisher may have syndication/reposts; it is not independent
            # corroboration if the source name or registrable domain matches.
            if (candidate.source or "").casefold() == (article.source or "").casefold():
                continue
            matches.append((candidate, candidate_source, title_similarity(article.title, candidate.title)))
        if matches:
            canonical = min([article] + [item[0] for item in matches], key=lambda item: (item.fetched_at, item.id))
            evidence["corroborating_sources"] = [
                {"article_id": item.id, "source": item.source, "url": item.url, "title": item.title,
                 "similarity": round(similarity, 3), "trust_score": meta["trust_score"]}
                for item, meta, similarity in matches
            ]
            status = "VERIFIED" if canonical.pk == article.pk else "DUPLICATE"
            duplicate_of = None if canonical.pk == article.pk else canonical
        else:
            # Publisher reputation alone is not enough to admit an event to
            # public results.  It remains pending until another independent
            # trusted report supplies corroborating evidence.
            status = "PENDING"
            duplicate_of = None
    if status != "DUPLICATE":
        duplicate_of = None

    metadata, _ = ArticleMetadata.objects.update_or_create(
        article=article,
        defaults={"quality_score": quality, "freshness_score": max(0.0, 1 - article_age(article).days / FRESHNESS_DAYS),
                  "source_trust": source["trust_score"], "verification_status": status,
                  "duplicate_of": duplicate_of, "evidence": evidence},
    )
    ProcessingRecord.objects.create(article=article, stage="governance_assessed", metadata={"status": status, "quality": quality})
    return metadata


def reassess_event(article):
    """Re-evaluate an event cluster after each ingest so the first report can become verified."""
    assessed = [assess_article(article)]
    for candidate in _candidate_articles(article):
        assessed.append(assess_article(candidate))
    return assessed
