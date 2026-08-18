"""
Single Gemini configuration boundary, replacing the 4 duplicated
`_ensure_configured()` copies in the original capston_end modules
(summarizer.py, insight_generator.py, answer_generator.py, adaptive_rag.py).
"""
import logging

import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger("news_agent.gemini_client")

_configured = False


def ensure_configured():
    global _configured
    if not _configured:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Export it or put it in capston_end/.env.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _configured = True


def get_model(model_name=None):
    ensure_configured()
    return genai.GenerativeModel(model_name or settings.GEMINI_MODEL)
