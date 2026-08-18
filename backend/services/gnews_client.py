"""Thin client around the GNews /top-headlines endpoint. Ported verbatim from capston_end."""
import logging
import time
from typing import Dict, List

import requests
from django.conf import settings

logger = logging.getLogger("news_agent.gnews")

GNEWS_CATEGORIES = [
    "general", "world", "nation", "business", "technology",
    "entertainment", "sports", "science", "health",
]


class GNewsClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GNEWS_API_KEY
        if not self.api_key:
            raise ValueError("GNEWS_API_KEY is not set. Export it or put it in capston_end/.env.")
        self.session = requests.Session()

    def fetch_by_category(self, category: str, lang: str = None, country: str = None, max_results: int = 10) -> List[Dict]:
        if category not in GNEWS_CATEGORIES:
            raise ValueError(f"Unknown category '{category}'. Valid: {GNEWS_CATEGORIES}")

        params = {
            "category": category,
            "lang": lang or settings.GNEWS_LANG,
            "country": country or settings.GNEWS_COUNTRY,
            "max": max_results,
            "apikey": self.api_key,
        }

        url = f"{settings.GNEWS_BASE_URL}/top-headlines"
        logger.info("Fetching GNews category=%s max=%s", category, max_results)

        resp = self.session.get(url, params=params, timeout=15)
        if resp.status_code == 403:
            raise RuntimeError("GNews returned 403 — check your API key / quota (free tier: 100 req/day).")
        resp.raise_for_status()

        data = resp.json()
        articles = data.get("articles", [])
        for a in articles:
            a["_category"] = category
        return articles

    def fetch_all_categories(self, categories: List[str] = None, max_results: int = 10) -> Dict[str, List[Dict]]:
        categories = categories or GNEWS_CATEGORIES
        results = {}
        for i, cat in enumerate(categories):
            try:
                results[cat] = self.fetch_by_category(cat, max_results=max_results)
            except Exception as e:
                logger.error("Failed to fetch category %s: %s", cat, e)
                results[cat] = []
            if i < len(categories) - 1:
                time.sleep(settings.REQUEST_DELAY_SECONDS)
        return results
