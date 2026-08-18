from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("articles", "0005_sourceregistry_ordering"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="processingrecord",
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="AuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(max_length=96)),
                ("resource_type", models.CharField(blank=True, max_length=64)),
                ("resource_id", models.CharField(blank=True, max_length=96)),
                ("request_id", models.CharField(blank=True, db_index=True, max_length=64)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.AddIndex(
            model_name="auditevent",
            index=models.Index(fields=["event_type", "created_at"], name="idx_audit_event_time"),
        ),
    ]
