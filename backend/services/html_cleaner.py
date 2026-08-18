"""Cleaning stage: strip stray HTML and normalize whitespace. Ported verbatim from capston_end."""
import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger("news_agent.html_cleaner")


def clean_html(text: str) -> str:
    if not text or not text.strip():
        return ""

    try:
        soup = BeautifulSoup(text, "html.parser")
        cleaned = soup.get_text(separator=" ")
    except Exception as e:
        logger.warning("HTML cleaning failed, using raw text: %s", e)
        cleaned = text

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
