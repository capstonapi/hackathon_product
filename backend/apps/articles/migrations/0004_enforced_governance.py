from django.db import migrations, models
import django.db.models.deletion


DEFAULT_SOURCES = [
    ("Reuters", "reuters.com", "reputable_news", 2, 2),
    ("Associated Press", "apnews.com", "reputable_news", 2, 2),
    ("BBC", "bbc.com", "reputable_news", 2, 2),
    ("BBC News", "bbc.com", "reputable_news", 2, 2),
    ("NASA", "nasa.gov", "official", 1, 1),
    ("The Guardian", "theguardian.com", "reputable_news", 2, 2),
    ("NPR", "npr.org", "reputable_news", 2, 2),
]


def seed_source_registry(apps, schema_editor):
    SourceRegistry = apps.get_model("articles", "SourceRegistry")
    for source, domain, source_type, tier, priority in DEFAULT_SOURCES:
        SourceRegistry.objects.update_or_create(source=source, defaults={
            "domain": domain, "source_type": source_type, "trust_tier": tier,
            "priority": priority, "active": True,
        })


class Migration(migrations.Migration):
    dependencies = [("articles", "0003_intelligence_governance")]

    operations = [
        migrations.AddField(
            model_name="articlemetadata", name="duplicate_of",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name="duplicate_articles", to="articles.article"),
        ),
        migrations.AddField(
            model_name="articlemetadata", name="evidence", field=models.JSONField(blank=True, default=dict),
        ),
        migrations.RunPython(seed_source_registry, migrations.RunPython.noop),
    ]
