"""
Insight generation stage: current article + retrieved similar articles ->
Gemini (JSON mode) -> {background, timeline, importance, expected_impact}.
Ported from capston_end/insight_generator.py, now via gemini_client.
"""
import json
import logging

from django.conf import settings

from .gemini_client import get_model

logger = logging.getLogger("news_agent.insight_generator")

INSIGHT_FIELDS = ["background", "timeline", "importance", "expected_impact"]


def _format_similar_article(article: dict) -> str:
    body = (article.get("summary") or "").strip()
    if not body:
        body = (article.get("content") or "")[:300].strip()
    return (
        f"- \"{article.get('title')}\" ({article.get('source') or 'unknown source'}, "
        f"{article.get('published_at') or 'date unknown'}): {body}"
    )


def _build_prompt(article: dict, similar_articles: list) -> str:
    current_body = (article.get("content") or article.get("summary") or "").strip()

    if similar_articles:
        context_block = "\n".join(_format_similar_article(a) for a in similar_articles)
    else:
        context_block = (
            "(No similar past articles were found in the archive -- this "
            "appears to be the first coverage of this topic.)"
        )

    return f"""You are a news analyst. You are given today's article and a set of \
related articles retrieved from an archive of past coverage on similar topics.

Using ONLY the information given below, produce a JSON object with exactly these \
four keys, each a short paragraph (2-4 sentences):

- "background": what led up to today's article -- prior context from the related \
articles, if any. If no related articles are provided, say so plainly instead of \
inventing history.
- "timeline": a chronological account of events, ordered from earliest to most \
recent, based on the published dates of the related articles and today's article.
- "importance": why today's article matters right now.
- "expected_impact": what is likely to happen next or who/what is affected.

Do not speculate beyond what the provided text supports. Do not fabricate dates, \
names, or events that are not present in the given articles.

Today's article -- "{article.get('title')}" ({article.get('source') or 'unknown source'}, \
{article.get('published_at') or 'date unknown'}):
{current_body[: settings.MAX_CHARS_FOR_SUMMARY]}

Related past articles:
{context_block}

Respond with only the JSON object."""


def generate_insights(article: dict, similar_articles: list) -> dict:
    content = (article.get("content") or article.get("summary") or "").strip()
    if not content:
        return {}

    try:
        model = get_model()
        prompt = _build_prompt(article, similar_articles)
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        parsed = json.loads(response.text)

        return {
            field: parsed[field].strip()
            for field in INSIGHT_FIELDS
            if isinstance(parsed.get(field), str) and parsed[field].strip()
        }
    except Exception as e:
        logger.error("Insight generation failed for '%s': %s", article.get("title"), e)
        return {}
