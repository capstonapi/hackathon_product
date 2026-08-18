from rest_framework import serializers

from .models import Article


class ArticleListSerializer(serializers.ModelSerializer):
    verification = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = [
            "id", "category", "title", "description", "url", "source",
            "published_at", "image_url", "summary", "fetched_at", "verification",
        ]

    def get_verification(self, obj):
        metadata = obj.active_metadata
        return {"status": metadata.verification_status, "source_trust": metadata.source_trust,
                "corroborating_sources": metadata.evidence.get("corroborating_sources", [])}


class ArticleDetailSerializer(serializers.ModelSerializer):
    has_insights = serializers.SerializerMethodField()
    claims = serializers.SerializerMethodField()
    verification = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id", "category", "title", "description", "content", "url", "source",
            "published_at", "image_url", "summary", "entities", "keywords",
            "extraction_method", "authors", "background", "timeline", "importance",
            "expected_impact", "context_article_ids", "fetched_at", "has_insights", "claims", "verification",
        ]

    def get_has_insights(self, obj):
        return any([obj.background, obj.timeline, obj.importance, obj.expected_impact])

    def get_claims(self, obj):
        from services.claims import extract_article_claims
        return [{"id": c.id, "text": c.text, "status": c.status, "evidence": [{"source": e.source, "title": e.title, "url": e.url, "excerpt": e.excerpt, "stance": e.stance, "retrieved_at": e.retrieved_at.isoformat()} for e in c.evidence.all()]} for c in extract_article_claims(obj)]

    def get_verification(self, obj):
        metadata = obj.active_metadata
        return {"status": metadata.verification_status, "source_trust": metadata.source_trust,
                "quality_score": metadata.quality_score, "freshness_score": metadata.freshness_score,
                "corroborating_sources": metadata.evidence.get("corroborating_sources", [])}


class RelatedArticleSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True, allow_null=True)

    class Meta:
        model = Article
        fields = ["id", "title", "source", "published_at", "url", "summary", "distance"]
