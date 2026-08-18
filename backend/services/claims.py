"""Evidence-based claim verification using independently governed coverage.

This module deliberately does not label a story "true" or "fake".  It stores
the evidence found for each extracted claim and reports whether that evidence
supports, contradicts, or is insufficient to assess the claim.
"""
import re

from django.db import DatabaseError, OperationalError, ProgrammingError

from apps.articles.models import Article, Claim, ClaimEvidence


CONTRADICTION_CUES = {
    "false", "fake", "hoax", "incorrect", "misleading", "denied",
    "denies", "deny", "refuted", "refutes", "debunked", "debunks",
}


def _sentences(text):
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text or "") if sentence.strip()]


def _terms(text):
    """Meaningful terms used only for transparent lexical evidence matching."""
    return {
        term for term in re.findall(r"[a-z0-9]{3,}", (text or "").lower())
        if term not in {"with", "from", "that", "this", "after", "will", "over", "news", "the", "and", "for"}
    }


def _best_evidence_sentence(claim_text, article_text):
    """Return the most relevant sentence and its claim-term coverage."""
    claim_terms = _terms(claim_text)
    if not claim_terms:
        return "", 0.0
    best_sentence, best_coverage = "", 0.0
    for sentence in _sentences(article_text):
        coverage = len(claim_terms & _terms(sentence)) / len(claim_terms)
        if coverage > best_coverage:
            best_sentence, best_coverage = sentence, coverage
    return best_sentence, best_coverage


def get_claim_evidence(claim_id):
    claim = Claim.objects.prefetch_related("evidence").get(pk=int(claim_id))
    return {"claim": claim.text, "status": claim.status, "evidence": [
        {"source": e.source, "title": e.title, "url": e.url, "excerpt": e.excerpt, "stance": e.stance, "retrieved_at": e.retrieved_at.isoformat()}
        for e in claim.evidence.all()
    ]}


def verify_article_claims(article, *, refresh=False):
    """Extract claims and classify them only from independent governed coverage.

    A claim starts as ``INSUFFICIENT_EVIDENCE``.  It becomes ``SUPPORTED`` only
    when another article in the governance corroboration record covers at
    least 45% of its meaningful terms.  Explicit refutation language in that
    matching coverage is recorded as ``CONTRADICTED``; competing evidence is
    ``MIXED``.  This is a transparent signal, not an assertion of absolute
    truth.
    """
    try:
        text = article.content or article.summary or ""
        claims = list(article.claims.all())
        if claims and not refresh:
            return article.claims.prefetch_related("evidence").all()
        if not claims:
            candidates = [sentence for sentence in _sentences(text) if len(sentence.split()) >= 7][:5]
            claims = [Claim.objects.create(article=article, text=candidate) for candidate in candidates]
        corroboration = article.active_metadata.evidence.get("corroborating_sources", [])
        for claim in claims:
            claim.evidence.all().delete()
            stances = set()
            for item in corroboration:
                other = Article.objects.filter(pk=item["article_id"]).first()
                other_text = (other.content or other.summary or "") if other else ""
                excerpt, coverage = _best_evidence_sentence(claim.text, other_text)
                if coverage >= 0.45:
                    stance = "contradicts" if _terms(excerpt) & CONTRADICTION_CUES else "supports"
                    ClaimEvidence.objects.create(claim=claim, source=item["source"], title=item["title"],
                        url=item["url"], excerpt=excerpt[:300], stance=stance)
                    stances.add(stance)
            if stances == {"supports"}:
                status = "SUPPORTED"
            elif stances == {"contradicts"}:
                status = "CONTRADICTED"
            elif stances:
                status = "MIXED"
            else:
                status = "INSUFFICIENT_EVIDENCE"
            claim.status = status
            claim.save(update_fields=["status"])
        return Claim.objects.filter(pk__in=[claim.pk for claim in claims]).prefetch_related("evidence")
    except (OperationalError, ProgrammingError, DatabaseError):
        # Existing deployments can serve articles safely before governance
        # migrations are applied; no verification status is inferred.
        return []


def extract_article_claims(article):
    """Read cached claim results for the detail serializer without rewriting them."""
    return verify_article_claims(article)
