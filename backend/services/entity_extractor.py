"""Entity extraction stage: cleaned text -> spaCy NER. Ported verbatim from capston_end."""
import logging
from typing import Dict, List

from django.conf import settings

logger = logging.getLogger("news_agent.entity_extractor")

_nlp = None


def _ensure_loaded():
    global _nlp
    if _nlp is None:
        import spacy

        _nlp = spacy.load(settings.SPACY_MODEL, disable=["lemmatizer"])
    return _nlp


def extract_entities(text: str) -> List[Dict]:
    if not text or not text.strip():
        return []

    try:
        nlp = _ensure_loaded()
        doc = nlp(text)
        seen = set()
        entities = []
        for ent in doc.ents:
            key = (ent.text.strip(), ent.label_)
            if key in seen or not key[0]:
                continue
            seen.add(key)
            entities.append({"text": key[0], "label": key[1]})
        return entities
    except Exception as e:
        logger.warning("Entity extraction failed: %s", e)
        return []
