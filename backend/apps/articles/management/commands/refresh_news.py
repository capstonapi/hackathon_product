from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ingest current headlines, then reassess current and historical governance status."

    def add_arguments(self, parser):
        parser.add_argument("--categories", default="nation,business,science,technology,sports,world")
        parser.add_argument("--max-per-category", type=int, default=5)
        parser.add_argument("--skip-insights", action="store_true")

    def handle(self, *args, **options):
        call_command(
            "fetch_news",
            categories=options["categories"],
            max_per_category=options["max_per_category"],
            skip_insights=options["skip_insights"],
        )
        call_command("reassess_news")
        call_command("generate_insights")
        self.stdout.write(self.style.SUCCESS("Refresh and historical governance reassessment complete."))
