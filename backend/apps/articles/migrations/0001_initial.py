import pgvector.django.indexes
import pgvector.django.vector
from django.db import migrations, models
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    """
    Maps the pre-existing `articles` table. Applied with --fake-initial so
    Django records it as applied without issuing CREATE TABLE/CREATE INDEX
    against data that already exists.
    """

    initial = True

    dependencies = []

    operations = [
        VectorExtension(),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.TextField()),
                ('title', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('url', models.TextField(unique=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('published_at', models.TextField(blank=True, null=True)),
                ('image_url', models.TextField(blank=True, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('entities', models.JSONField(blank=True, null=True)),
                ('keywords', models.JSONField(blank=True, null=True)),
                ('embedding', pgvector.django.vector.VectorField(blank=True, dimensions=768, null=True)),
                ('extraction_method', models.TextField(blank=True, null=True)),
                ('authors', models.JSONField(blank=True, null=True)),
                ('background', models.TextField(blank=True, null=True)),
                ('timeline', models.TextField(blank=True, null=True)),
                ('importance', models.TextField(blank=True, null=True)),
                ('expected_impact', models.TextField(blank=True, null=True)),
                ('context_article_ids', models.JSONField(blank=True, null=True)),
                ('fetched_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'articles',
                'ordering': ['-fetched_at'],
                'indexes': [
                    models.Index(fields=['category'], name='idx_articles_category'),
                    models.Index(fields=['fetched_at'], name='idx_articles_fetched_at'),
                    pgvector.django.indexes.HnswIndex(
                        ef_construction=64, fields=['embedding'], m=16,
                        name='idx_articles_embedding', opclasses=['vector_cosine_ops'],
                    ),
                ],
            },
        ),
    ]
