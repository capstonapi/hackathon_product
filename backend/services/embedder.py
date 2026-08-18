"""
Embedding stage: cleaned text -> Gemini embedContent -> vector.

Calls Gemini's REST endpoint directly with `requests` rather than the
google-generativeai SDK -- the SDK's gRPC transport hangs in this
environment trying to reach a GCE metadata service that doesn't exist here.
This is a preserved workaround, not a stylistic choice -- do not replace it
with `genai.embed_content()`.

gemini-embedding-001 defaults to 3072 dimensions, but pgvector's HNSW index
caps at 2000, so we request a truncated size via outputDimensionality.
Truncated embeddings are NOT pre-normalized, so we L2-normalize the result
ourselves to keep cosine similarity meaningful.
"""
import logging
import math
import hashlib
from typing import List, Optional

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("news_agent.embedder")

EMBED_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"


def _l2_normalize(vector: List[float]) -> List[float]:
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Returns an L2-normalized embedding vector, or None on empty input or
    failure. Never raises -- callers treat a missing embedding as "exclude
    from similarity search".
    """
    if not text or not text.strip():
        return None

    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set, skipping embedding")
        return None

    trimmed = text[: settings.MAX_CHARS_FOR_SUMMARY]
    cache_key = f"embedding:{settings.EMBEDDING_MODEL}:{hashlib.sha256(trimmed.encode()).hexdigest()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    url = EMBED_URL_TEMPLATE.format(model=settings.EMBEDDING_MODEL)

    try:
        resp = requests.post(
            url,
            params={"key": settings.GEMINI_API_KEY},
            json={
                "content": {"parts": [{"text": trimmed}]},
                "outputDimensionality": settings.EMBEDDING_DIM,
            },
            timeout=30,
        )
        resp.raise_for_status()
        values = resp.json()["embedding"]["values"]
        vector = _l2_normalize(values)
        cache.set(cache_key, vector, timeout=60 * 60 * 24)
        return vector
    except Exception as e:
        logger.error("Embedding generation failed: %s", e)
        return None
