from django.urls import path

from .views import SourcesView

urlpatterns = [
    path("", SourcesView.as_view(), name="sources-list"),
]
