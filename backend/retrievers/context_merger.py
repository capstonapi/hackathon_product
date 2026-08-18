from .base import Document


class ContextMerger:
    """Deduplicates context and keeps trusted factual sources at the top. Ported verbatim from capston_end."""

    def merge(self, documents: list[Document], limit: int = 6) -> list[Document]:
        unique = {}
        for document in documents:
            key = document.url or f"{document.source}:{document.title}"
            if key not in unique or document.relevance_score > unique[key].relevance_score:
                unique[key] = document
        # Relevance leads; source trust and freshness metadata act as explicit tie breakers.
        return sorted(unique.values(), key=lambda d: (d.relevance_score * .7 + d.trust_score * .3, d.published_at), reverse=True)[:limit]
