from django.db import migrations


TRUSTED_SOURCES = [
    ("BBC News", "bbc.com"), ("NPR", "npr.org"), ("PBS News", "pbs.org"),
    ("PBS NewsHour", "pbs.org"), ("CBS News", "cbsnews.com"),
    ("ABC News", "abcnews.go.com"), ("NBC News", "nbcnews.com"),
    ("USA Today", "usatoday.com"), ("Los Angeles Times", "latimes.com"),
    ("Agence France-Presse", "afp.com"), ("AFP", "afp.com"),
    ("Bloomberg", "bloomberg.com"), ("Politico", "politico.com"),
    ("Axios", "axios.com"), ("The Economist", "economist.com"),
    ("Al Jazeera", "aljazeera.com"), ("CBC", "cbc.ca"),
    ("CBC News", "cbc.ca"), ("Deutsche Welle", "dw.com"),
    ("France 24", "france24.com"), ("The Straits Times", "straitstimes.com"),
    ("Nikkei Asia", "asia.nikkei.com"), ("The Japan Times", "japantimes.co.jp"),
    ("Press Trust of India", "ptinews.com"),
]

OFFICIAL_SOURCES = [
    ("The White House", "whitehouse.gov"), ("United Nations", "un.org"),
    ("World Health Organization", "who.int"),
    ("Centers for Disease Control and Prevention", "cdc.gov"),
    ("European Commission", "europa.eu"),
]


def seed_trusted_sources(apps, schema_editor):
    SourceRegistry = apps.get_model("articles", "SourceRegistry")
    for source, domain in TRUSTED_SOURCES:
        SourceRegistry.objects.update_or_create(
            source=source,
            defaults={"domain": domain, "source_type": "reputable_news", "trust_tier": 2, "priority": 2, "active": True},
        )
    for source, domain in OFFICIAL_SOURCES:
        SourceRegistry.objects.update_or_create(
            source=source,
            defaults={"domain": domain, "source_type": "official", "trust_tier": 1, "priority": 1, "active": True},
        )


class Migration(migrations.Migration):
    dependencies = [("articles", "0006_auditevent_and_lineage_ordering")]

    operations = [migrations.RunPython(seed_trusted_sources, migrations.RunPython.noop)]
