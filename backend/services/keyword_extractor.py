"""Keyword extraction stage: spaCy noun chunks ranked by frequency. Ported verbatim from capston_end."""
import logging
from collections import Counter
from typing import List

from django.conf import settings

logger = logging.getLogger("news_agent.keyword_extractor")

_nlp = None


def _ensure_loaded():
    global _nlp
    if _nlp is None:
        import spacy

        _nlp = spacy.load(settings.SPACY_MODEL, disable=["lemmatizer"])
    return _nlp


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    if not text or not text.strip():
        return []

    try:
        nlp = _ensure_loaded()
        doc = nlp(text)

        counts = Counter()
        for chunk in doc.noun_chunks:
            phrase = " ".join(
                tok.text.lower() for tok in chunk if not tok.is_stop and not tok.is_punct and tok.is_alpha
            ).strip()
            if len(phrase) > 2:
                counts[phrase] += 1

        return [phrase for phrase, _ in counts.most_common(top_n)]
    except Exception as e:
        logger.warning("Keyword extraction failed: %s", e)
        return []
