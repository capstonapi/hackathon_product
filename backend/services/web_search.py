"""External knowledge base search: Google News RSS, Wikipedia, DuckDuckGo. Ported verbatim from capston_end."""
import logging
from typing import Dict, List
from urllib.parse import quote

import requests
from django.core.cache import cache

logger = logging.getLogger("news_agent.web_search")

GOOGLE_NEWS_BASE_URL = "https://news.google.com/rss/search"
WIKIPEDIA_BASE_URL = "https://en.wikipedia.org/w/api.php"


def search_google_news(query: str, max_results: int = 3) -> List[Dict]:
    try:
        import feedparser
    except ImportError:
        logger.warning("feedparser not installed, skipping Google News search")
        return []

    try:
        feed = feedparser.parse(f"{GOOGLE_NEWS_BASE_URL}?q={quote(query)}")
        return [
            {
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published_at": entry.get("published", ""),
                "source": "Google News",
                "summary": entry.get("summary", "")[:200],
            }
            for entry in feed.entries[:max_results]
        ]
    except Exception as e:
        logger.warning("external_api_failed provider=google_news error=%s", type(e).__name__)
        return []


def search_wikipedia(query: str, max_results: int = 2) -> List[Dict]:
    cache_key = f"external:wikipedia:{query.lower().strip()}:{max_results}"
    if cached := cache.get(cache_key):
        return cached
    try:
        params = {"action": "query", "format": "json", "list": "search", "srsearch": query, "srlimit": max_results}
        response = requests.get(
            WIKIPEDIA_BASE_URL, params=params,
            headers={"User-Agent": "NewsAgentRAG/1.0 (educational project)"}, timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        results = [
            {
                "title": item.get("title", ""),
                "url": f"https://en.wikipedia.org/wiki/{quote(item.get('title', ''))}",
                "summary": item.get("snippet", "")[:300],
                "source": "Wikipedia",
            }
            for item in data.get("query", {}).get("search", [])
        ]
        cache.set(cache_key, results, timeout=60 * 30)
        return results
    except Exception as e:
        logger.warning("external_api_failed provider=wikipedia error=%s", type(e).__name__)
        return []


def search_web(query: str, max_results: int = 3) -> List[Dict]:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        logger.warning("duckduckgo_search not installed, skipping web search")
        return []

    try:
        ddgs = DDGS()
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "summary": item.get("body", "")[:300],
                "source": "Web Search",
            }
            for item in ddgs.text(query, max_results=max_results)
        ]
    except Exception as e:
        logger.warning("external_api_failed provider=web error=%s", type(e).__name__)
        return []


def search_external_knowledge_base(
    query: str, use_news: bool = True, use_wikipedia: bool = True, use_web: bool = True,
    max_results_per_source: int = 2,
) -> List[Dict]:
    cache_key = f"external:merged:{query.lower().strip()}:{max_results_per_source}"
    if cached := cache.get(cache_key):
        return cached
    all_results = []
    if use_news:
        all_results.extend(search_google_news(query, max_results=max_results_per_source))
    if use_wikipedia:
        all_results.extend(search_wikipedia(query, max_results=max_results_per_source))
    if use_web:
        all_results.extend(search_web(query, max_results=max_results_per_source))

    seen_urls = set()
    deduped = []
    for result in all_results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduped.append(result)

    logger.info("external_retrieval_complete sources=%d", len(deduped))
    cache.set(cache_key, deduped, timeout=60 * 15)
    return deduped
