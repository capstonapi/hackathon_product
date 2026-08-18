from django.db.models import Count

from apps.articles.governance import verified_articles


def get_sources():
    rows = (
        verified_articles().exclude(source__isnull=True)
        .exclude(source="")
        .values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return list(rows)
