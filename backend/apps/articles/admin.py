from django.contrib import admin

from .models import ArticleMetadata, Claim, ClaimEvidence, ProcessingRecord, SourceRegistry

admin.site.register(SourceRegistry)
admin.site.register(ArticleMetadata)
admin.site.register(Claim)
admin.site.register(ClaimEvidence)
admin.site.register(ProcessingRecord)

from .models import Article, SavedArticle


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "category", "title", "source", "fetched_at"]
    list_filter = ["category"]
    search_fields = ["title", "url"]
    exclude = ["embedding"]


@admin.register(SavedArticle)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "article", "created_at"]
