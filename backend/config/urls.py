from django.contrib import admin
from django.urls import include, path

from apps.articles.views import CategoriesView, SavedArticlesListView
from apps.chat.views import HistoryView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/articles/", include("apps.articles.urls")),
    path("api/saved/", SavedArticlesListView.as_view(), name="saved-articles"),
    path("api/history/", HistoryView.as_view(), name="chat-history"),
    path("api/chat/", include("apps.chat.urls")),
    path("api/categories/", CategoriesView.as_view(), name="categories"),
    path("api/sources/", include("apps.sources.urls")),
]
