"""
Full-article extraction stage. Ported verbatim from capston_end: trafilatura
first, newspaper3k fallback, GNews's own text as a last resort.
"""
import logging
from typing import Dict, Optional

import trafilatura

logger = logging.getLogger("news_agent.extractor")

MIN_ACCEPTABLE_LENGTH = 400  # chars; below this we treat extraction as "failed"


def _extract_with_trafilatura(url: str) -> Optional[str]:
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        return trafilatura.extract(
            downloaded, include_comments=False, include_tables=False, favor_precision=True
        )
    except Exception as e:
        logger.warning("trafilatura failed for %s: %s", url, e)
        return None


def _extract_with_newspaper(url: str) -> Optional[Dict]:
    try:
        from newspaper import Article  # lazy import -- heavier dependency

        art = Article(url)
        art.download()
        art.parse()
        if not art.text:
            return None
        return {
            "text": art.text,
            "authors": art.authors,
            "publish_date": str(art.publish_date) if art.publish_date else None,
            "top_image": art.top_image,
        }
    except Exception as e:
        logger.warning("newspaper3k failed for %s: %s", url, e)
        return None


def extract_article(url: str, fallback_text: str = "") -> Dict:
    text = _extract_with_trafilatura(url)
    if text and len(text) >= MIN_ACCEPTABLE_LENGTH:
        return {"text": text, "authors": [], "publish_date": None, "extraction_method": "trafilatura"}

    logger.info("trafilatura result too short/empty for %s, trying newspaper3k", url)
    np_result = _extract_with_newspaper(url)
    if np_result and len(np_result["text"]) >= MIN_ACCEPTABLE_LENGTH:
        np_result["extraction_method"] = "newspaper3k"
        return np_result

    best_effort = text or fallback_text or ""
    return {"text": best_effort, "authors": [], "publish_date": None, "extraction_method": "fallback"}
