"""
Ingestion command: GNews -> extract -> clean -> summarize -> NLP -> embed -> save.

This is the orchestrator that was missing from the Django port -- the
`services` module documents each stage but nothing previously called them
in sequence. Wires them together against the `Article` model.
"""
import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.articles import services
from apps.articles.governance import reassess_event
from apps.articles.models import Article, ProcessingRecord
from services.embedder import generate_embedding
from services.entity_extractor import extract_entities
from services.extractor import extract_article
from services.gnews_client import GNewsClient
from services.html_cleaner import clean_html
from services.insight_generator import generate_insights
from services.keyword_extractor import extract_keywords
from services.claims import verify_article_claims
from services.summarizer import summarize_with_gemini

logger = logging.getLogger("news_agent.fetch_news")

DEFAULT_CATEGORIES = ["nation", "business", "science", "technology", "sports", "world"]


class Command(BaseCommand):
    help = "Fetch top headlines from GNews, enrich them, and store them as Articles."

    def add_arguments(self, parser):
        parser.add_argument(
            "--categories",
            default=",".join(DEFAULT_CATEGORIES),
            help=f"Comma-separated GNews categories. Default: {','.join(DEFAULT_CATEGORIES)}",
        )
        parser.add_argument("--max-per-category", type=int, default=10)
        parser.add_argument(
            "--skip-insights",
            action="store_true",
            help="Skip the background/timeline/importance/expected_impact Gemini call (faster, fewer API calls).",
        )

    def handle(self, *args, **options):
        categories = [c.strip() for c in options["categories"].split(",") if c.strip()]
        max_results = options["max_per_category"]
        skip_insights = options["skip_insights"]

        client = GNewsClient()
        by_category = client.fetch_all_categories(categories=categories, max_results=max_results)

        created = 0
        skipped = 0
        failed = 0

        for category, raw_articles in by_category.items():
            for raw in raw_articles:
                url = raw.get("url")
                if not url:
                    continue
                if Article.objects.filter(url=url).exists():
                    skipped += 1
                    continue

                try:
                    self._ingest_one(category, raw, skip_insights=skip_insights)
                    created += 1
                except Exception:
                    logger.exception("Failed to ingest article %s", url)
                    failed += 1

                time.sleep(settings.REQUEST_DELAY_SECONDS)

        self.stdout.write(
            self.style.SUCCESS(f"Done. created={created} skipped_existing={skipped} failed={failed}")
        )

    def _ingest_one(self, category, raw, skip_insights):
        title = raw.get("title") or ""
        description = clean_html(raw.get("description") or "")
        source_name = (raw.get("source") or {}).get("name")

        extracted = extract_article(raw["url"], fallback_text=raw.get("content") or description)
        text = clean_html(extracted["text"])

        summary = summarize_with_gemini(title, text or description)
        entities = extract_entities(text)
        keywords = extract_keywords(text)
        embedding = generate_embedding(text or summary or description)

        article = Article.objects.create(
            category=category,
            title=title,
            description=description,
            content=text,
            url=raw["url"],
            source=source_name,
            published_at=raw.get("publishedAt"),
            image_url=raw.get("image"),
            summary=summary,
            entities=entities,
            keywords=keywords,
            embedding=embedding,
            extraction_method=extracted.get("extraction_method"),
            authors=extracted.get("authors") or [],
        )
        ProcessingRecord.objects.bulk_create([
            ProcessingRecord(article=article, stage="ingested", metadata={"category": category, "source": source_name or "", "url": raw["url"]}),
            ProcessingRecord(article=article, stage="content_extracted", metadata={"method": extracted.get("extraction_method") or "fallback", "content_characters": len(text)}),
            ProcessingRecord(article=article, stage="summary_generated", metadata={"summary_characters": len(summary or "")}),
            ProcessingRecord(article=article, stage="embedding_generated", metadata={"available": embedding is not None}),
        ])

        if not skip_insights and embedding is not None:
            similar = list(
                services.find_similar_by_embedding(embedding, exclude_article_id=article.id, limit=5)
            )
            if similar:
                insights = generate_insights(
                    {
                        "title": title,
                        "source": source_name,
                        "published_at": article.published_at,
                        "content": text,
                        "summary": summary,
                    },
                    [
                        {
                            "title": a.title,
                            "source": a.source,
                            "published_at": a.published_at,
                            "summary": a.summary,
                            "content": a.content,
                        }
                        for a in similar
                    ],
                )
                if insights:
                    for field, value in insights.items():
                        setattr(article, field, value)
                    article.context_article_ids = [a.id for a in similar]
                    article.save(update_fields=list(insights.keys()) + ["context_article_ids"])

        reassess_event(article)
        verify_article_claims(article, refresh=True)
        return article
