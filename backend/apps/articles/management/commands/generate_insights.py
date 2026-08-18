from django.core.management.base import BaseCommand

from apps.articles import services
from apps.articles.governance import verified_articles
from apps.articles.models import ProcessingRecord
from services.insight_generator import generate_insights


class Command(BaseCommand):
    help = "Generate background, timeline, importance, and impact for verified articles."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Regenerate existing insights.")

    def handle(self, *args, **options):
        updated = 0
        skipped = 0
        for article in verified_articles().order_by("id"):
            if not options["force"] and all([
                article.background, article.timeline, article.importance, article.expected_impact,
            ]):
                skipped += 1
                continue
            similar = list(services.find_similar_by_embedding(article.embedding, exclude_article_id=article.id, limit=5)) if article.embedding is not None else []
            insights = generate_insights(
                {
                    "title": article.title,
                    "source": article.source,
                    "published_at": article.published_at,
                    "content": article.content,
                    "summary": article.summary,
                },
                [
                    {"title": item.title, "source": item.source, "published_at": item.published_at,
                     "content": item.content, "summary": item.summary}
                    for item in similar
                ],
            )
            if not insights:
                self.stderr.write(f"No insights generated for article {article.id}; it will remain in the retry queue.")
                continue
            for field, value in insights.items():
                setattr(article, field, value)
            article.context_article_ids = [item.id for item in similar]
            article.save(update_fields=[*insights.keys(), "context_article_ids"])
            ProcessingRecord.objects.create(
                article=article,
                stage="insights_generated",
                metadata={"related_article_ids": article.context_article_ids, "fields": sorted(insights)},
            )
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Insights updated={updated}, already_complete={skipped}"))
