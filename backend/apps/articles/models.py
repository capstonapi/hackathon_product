from django.conf import settings
from django.db import models
from pgvector.django import HnswIndex, VectorField


class Article(models.Model):
    """
    Maps the existing `articles` table 1:1 (see capston_end/storage.py's
    SCHEMA) -- this app does not own ingestion writes, only reads. The
    initial migration is applied with --fake-initial so Django never issues
    CREATE TABLE/CREATE INDEX against data that already exists.
    """

    id = models.AutoField(primary_key=True)
    category = models.TextField()
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    url = models.TextField(unique=True)
    source = models.TextField(null=True, blank=True)
    published_at = models.TextField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    entities = models.JSONField(null=True, blank=True)
    keywords = models.JSONField(null=True, blank=True)
    embedding = VectorField(dimensions=settings.EMBEDDING_DIM, null=True, blank=True)
    extraction_method = models.TextField(null=True, blank=True)
    authors = models.JSONField(null=True, blank=True)
    background = models.TextField(null=True, blank=True)
    timeline = models.TextField(null=True, blank=True)
    importance = models.TextField(null=True, blank=True)
    expected_impact = models.TextField(null=True, blank=True)
    context_article_ids = models.JSONField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "articles"
        ordering = ["-fetched_at"]
        indexes = [
            models.Index(fields=["category"], name="idx_articles_category"),
            models.Index(fields=["fetched_at"], name="idx_articles_fetched_at"),
            HnswIndex(
                name="idx_articles_embedding",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return self.title


class SavedArticle(models.Model):
    """A user's bookmark of an article -- brand-new table, no legacy data."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_articles")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")
        ordering = ["-created_at"]


class SourceRegistry(models.Model):
    """Configurable source policy; retrieval code never owns a source allowlist."""
    SOURCE_TYPES = [("official", "Official"), ("reputable_news", "Highly reputable news"), ("reference", "Reference"), ("general_news", "Reputable general news"), ("web", "General web")]
    source = models.CharField(max_length=160, unique=True)
    domain = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(max_length=32, choices=SOURCE_TYPES, default="web")
    trust_tier = models.PositiveSmallIntegerField(default=5)
    priority = models.PositiveSmallIntegerField(default=5)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["priority", "source"]


class ArticleMetadata(models.Model):
    """Active quality metadata kept outside the legacy articles table."""
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name="active_metadata")
    quality_score = models.FloatField(default=0.0)
    freshness_score = models.FloatField(default=0.0)
    source_trust = models.FloatField(default=0.0)
    verification_status = models.CharField(max_length=32, default="UNVERIFIED")
    # A canonical article represents an event in the public feed.  Other
    # coverage of the same event is retained as auditable corroboration.
    duplicate_of = models.ForeignKey(Article, null=True, blank=True, on_delete=models.SET_NULL, related_name="duplicate_articles")
    evidence = models.JSONField(default=dict, blank=True)
    retrieved_at = models.DateTimeField(auto_now=True)


class Claim(models.Model):
    STATUSES = [("SUPPORTED", "Supported"), ("CONTRADICTED", "Contradicted"), ("MIXED", "Mixed"), ("INSUFFICIENT_EVIDENCE", "Insufficient evidence")]
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="claims")
    text = models.TextField()
    status = models.CharField(max_length=32, choices=STATUSES, default="INSUFFICIENT_EVIDENCE")
    created_at = models.DateTimeField(auto_now_add=True)


class ClaimEvidence(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="evidence")
    source = models.CharField(max_length=255)
    title = models.TextField()
    url = models.URLField(max_length=1000)
    excerpt = models.TextField(blank=True)
    stance = models.CharField(max_length=16, choices=[("supports", "Supports"), ("contradicts", "Contradicts")])
    retrieved_at = models.DateTimeField(auto_now_add=True)


class ProcessingRecord(models.Model):
    """Append-only lineage for ingest/extraction/embedding/retrieval stages."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="processing_records", null=True, blank=True)
    stage = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class AuditEvent(models.Model):
    """Append-only operational audit trail for state-changing API requests.

    Payloads are deliberately metadata-only: passwords, tokens, questions,
    and article text must never be copied into an audit record.
    """
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_events")
    event_type = models.CharField(max_length=96)
    resource_type = models.CharField(max_length=64, blank=True)
    resource_id = models.CharField(max_length=96, blank=True)
    request_id = models.CharField(max_length=64, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["event_type", "created_at"], name="idx_audit_event_time")]
