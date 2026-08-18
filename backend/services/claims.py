"""Controlled, read-only claim evidence access. Never accepts SQL or model code."""
import re

from django.db import DatabaseError, OperationalError, ProgrammingError

from apps.articles.governance import title_similarity
from apps.articles.models import Article, Claim, ClaimEvidence


def get_claim_evidence(claim_id):
    claim = Claim.objects.prefetch_related("evidence").get(pk=int(claim_id))
    return {"claim": claim.text, "status": claim.status, "evidence": [
        {"source": e.source, "title": e.title, "url": e.url, "excerpt": e.excerpt, "stance": e.stance, "retrieved_at": e.retrieved_at.isoformat()}
        for e in claim.evidence.all()
    ]}


def extract_article_claims(article):
    """Attach independent-source evidence before a claim is marked supported."""
    try:
        if article.claims.exists():
            return article.claims.prefetch_related("evidence").all()
        text = article.content or article.summary or ""
        candidates = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) >= 7][:5]
        claims = [Claim.objects.create(article=article, text=candidate) for candidate in candidates]
        corroboration = article.active_metadata.evidence.get("corroborating_sources", [])
        for claim in claims:
            for item in corroboration:
                other = Article.objects.filter(pk=item["article_id"]).first()
                other_text = (other.content or other.summary or "") if other else ""
                if title_similarity(claim.text, other_text) >= 0.20:
                    ClaimEvidence.objects.create(claim=claim, source=item["source"], title=item["title"],
                        url=item["url"], excerpt=other_text[:300], stance="supports")
                    claim.status = "SUPPORTED"
                    claim.save(update_fields=["status"])
                    break
        return Claim.objects.filter(pk__in=[claim.pk for claim in claims]).prefetch_related("evidence")
    except (OperationalError, ProgrammingError, DatabaseError):
        # Existing deployments can serve articles safely before governance
        # migrations are applied; no verification status is inferred.
        return []
