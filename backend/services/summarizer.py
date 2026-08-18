"""Summary stage: article text -> Gemini -> concise summary. Ported from capston_end, now via gemini_client."""
import logging
import re

from django.conf import settings

from .gemini_client import get_model

logger = logging.getLogger("news_agent.summarizer")

SUMMARY_PROMPT = """You are a news editor. Summarize the following article in 3-4 concise, \
neutral sentences. Do not add opinion or speculation. Do not start with phrases \
like "This article discusses" — just state the facts directly.

Title: {title}

Article:
{text}

Summary:"""


def _fallback_summary(title: str, text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return title.strip() if title else ""

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
    # A publisher can block full-text extraction.  In that case GNews's
    # description is still useful, so retain a compact 2-3 sentence digest
    # instead of showing a bare headline in the product.
    summary = " ".join(sentences[:3]) if sentences else cleaned

    if len(summary) > 500:
        summary = summary[:497].rsplit(" ", 1)[0] + "..."

    if title and title.strip() and title.strip() not in summary:
        return f"{title.strip()}: {summary}"
    return summary


def summarize_with_gemini(title: str, text: str) -> str:
    if not text or not text.strip():
        return ""

    trimmed = text[: settings.MAX_CHARS_FOR_SUMMARY]
    prompt = SUMMARY_PROMPT.format(title=title, text=trimmed)

    try:
        response = get_model().generate_content(prompt)
        return (response.text or "").strip()
    except Exception as e:
        logger.error("Gemini summarization failed for '%s': %s", title, e)
        return _fallback_summary(title, trimmed)
