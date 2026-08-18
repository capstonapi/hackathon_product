from django.urls import path

from .views import (
    ArticleDetailView,
    ArticleListView,
    ArticleSearchView,
    LatestArticlesView,
    RelatedArticlesView,
    SaveArticleView,
    TimelineView,
)

urlpatterns = [
    path("latest/", LatestArticlesView.as_view(), name="article-latest"),
    path("search/", ArticleSearchView.as_view(), name="article-search"),
    path("<int:pk>/related/", RelatedArticlesView.as_view(), name="article-related"),
    path("<int:pk>/timeline/", TimelineView.as_view(), name="article-timeline"),
    path("<int:pk>/save/", SaveArticleView.as_view(), name="article-save"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),
    path("", ArticleListView.as_view(), name="article-list"),
]
