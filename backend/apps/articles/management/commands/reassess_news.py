from collections import Counter

from django.core.management.base import BaseCommand

from apps.articles.governance import reassess_event
from apps.articles.models import Article, ProcessingRecord
from services.claims import verify_article_claims


class Command(BaseCommand):
    help = "Reassess governance status for current and historical articles. Schedule this nightly."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=250)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        articles = Article.objects.order_by("id")
        totals = Counter()
        processed = 0
        for article in articles.iterator(chunk_size=options["batch_size"]):
            if options["dry_run"]:
                processed += 1
                continue
            records = reassess_event(article)
            claims = verify_article_claims(article, refresh=True)
            for record in records:
                totals[record.verification_status] += 1
            ProcessingRecord.objects.create(
                article=article,
                stage="governance_reassessed",
                metadata={"status": article.active_metadata.verification_status, "claims_checked": len(claims)},
            )
            processed += 1
        if options["dry_run"]:
            self.stdout.write(f"Dry run: {processed} historical articles would be reassessed.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Reassessed {processed} articles: {dict(totals)}"))
