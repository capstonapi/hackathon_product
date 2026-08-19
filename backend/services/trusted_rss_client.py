"""Fetch headlines directly from a curated set of publisher RSS feeds."""
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List

import feedparser
import requests
from django.conf import settings

logger = logging.getLogger("news_agent.trusted_rss")


class TrustedRSSClient:
    """Normalise trusted publisher RSS entries to the GNews article shape."""

    def _feed_configs(self):
        for value in settings.TRUSTED_RSS_FEEDS:
            try:
                source, category, url = value.split("|", 2)
            except ValueError:
                logger.warning("Ignoring malformed TRUSTED_RSS_FEEDS entry")
                continue
            yield source.strip(), category.strip(), url.strip()

    @staticmethod
    def _published(entry):
        value = entry.get("published") or entry.get("updated")
        if value:
            try:
                return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
            except (TypeError, ValueError):
                pass
        parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if parsed:
            return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
        return None

    def fetch_all_categories(self, categories: List[str] = None, max_results: int = 10) -> Dict[str, List[Dict]]:
        requested = set(categories or [])
        results = {category: [] for category in requested}
        seen_urls = set()

        for source, category, feed_url in self._feed_configs():
            if requested and category not in requested:
                continue
            try:
                response = requests.get(
                    feed_url,
                    headers={"User-Agent": "AI-News-Intelligence/1.0 (trusted RSS reader)"},
                    timeout=15,
                )
                response.raise_for_status()
                feed = feedparser.parse(response.content)
            except Exception as exc:
                logger.error("Failed to fetch trusted RSS feed source=%s: %s", source, exc)
                continue

            articles = results.setdefault(category, [])
            for entry in feed.entries:
                if len(articles) >= max_results:
                    break
                url = entry.get("link")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", entry.get("description", "")),
                    "content": entry.get("content", [{}])[0].get("value", "") if entry.get("content") else "",
                    "url": url,
                    "source": {"name": source},
                    "publishedAt": self._published(entry),
                    "image": None,
                    "_ingestion_source": "trusted_rss",
                })
        return results
