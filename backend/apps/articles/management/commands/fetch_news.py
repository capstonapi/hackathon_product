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
from apps.articles.source_policy import is_trusted_source
from services.embedder import generate_embedding
from services.entity_extractor import extract_entities
from services.extractor import extract_article
from services.gnews_client import GNewsClient
from services.html_cleaner import clean_html
from services.insight_generator import generate_insights
from services.keyword_extractor import extract_keywords
from services.claims import verify_article_claims
from services.summarizer import summarize_with_gemini
from services.trusted_rss_client import TrustedRSSClient

logger = logging.getLogger("news_agent.fetch_news")

DEFAULT_CATEGORIES = ["nation", "business", "science", "technology", "sports", "world"]


class Command(BaseCommand):
    help = "Fetch trusted headlines from GNews and/or direct publisher RSS feeds."

    def add_arguments(self, parser):
        parser.add_argument(
            "--categories",
            default=",".join(DEFAULT_CATEGORIES),
            help=f"Comma-separated GNews categories. Default: {','.join(DEFAULT_CATEGORIES)}",
        )
        parser.add_argument("--max-per-category", type=int, default=10)
        parser.add_argument(
            "--provider", choices=["auto", "gnews", "rss"], default="auto",
            help="auto uses GNews when available and direct trusted RSS feeds as a fallback.",
        )
        parser.add_argument(
            "--skip-insights",
            action="store_true",
            help="Skip the background/timeline/importance/expected_impact Gemini call (faster, fewer API calls).",
        )

    def handle(self, *args, **options):
        categories = [c.strip() for c in options["categories"].split(",") if c.strip()]
        max_results = options["max_per_category"]
        skip_insights = options["skip_insights"]

        by_category = {category: [] for category in categories}
        if options["provider"] in {"auto", "gnews"}:
            try:
                by_category = GNewsClient().fetch_all_categories(categories=categories, max_results=max_results)
            except ValueError as exc:
                if options["provider"] == "gnews":
                    raise
                logger.warning("GNews unavailable; using trusted RSS feeds: %s", exc)

        if options["provider"] == "rss" or (
            options["provider"] == "auto" and not any(by_category.values())
        ):
            by_category = TrustedRSSClient().fetch_all_categories(
                categories=categories, max_results=max_results
            )

        created = 0
        skipped = 0
        untrusted = 0
        failed = 0

        for category, raw_articles in by_category.items():
            for raw in raw_articles:
                url = raw.get("url")
                if not url:
                    continue
                source_name = (raw.get("source") or {}).get("name") or ""
                if not is_trusted_source(source_name, url):
                    logger.info("Skipping non-allowlisted publisher source=%s url=%s", source_name, url)
                    untrusted += 1
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
            self.style.SUCCESS(
                f"Done. created={created} skipped_existing={skipped} "
                f"skipped_untrusted={untrusted} failed={failed}"
            )
        )

    def _ingest_one(self, category, raw, skip_insights):
        title = raw.get("title") or ""
        description = clean_html(raw.get("description") or "")
        source_name = (raw.get("source") or {}).get("name")

        if raw.get("_ingestion_source") == "trusted_rss":
            # Many publishers allow their public RSS feed but block repeated
            # automated page downloads.  Use the text they explicitly
            # syndicated instead of turning a fast feed refresh into a series
            # of slow or blocked extraction requests.
            text = clean_html(raw.get("content") or description)
            extracted = {"text": text, "extraction_method": "trusted_rss"}
        else:
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
