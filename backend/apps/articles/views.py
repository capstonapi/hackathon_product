from rest_framework import status
from django.db import DatabaseError, OperationalError, ProgrammingError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.search.services import search_articles

from . import services
from .models import Article, ProcessingRecord
from .serializers import ArticleDetailSerializer, ArticleListSerializer, RelatedArticleSerializer


class ArticleListView(ListAPIView):
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        params = self.request.query_params
        return services.list_articles(
            category=params.get("category"),
            source=params.get("source"),
            date_from=params.get("date_from"),
            date_to=params.get("date_to"),
        )


class ArticleDetailView(APIView):
    def get(self, request, pk):
        article = services.get_article(pk)
        try:
            ProcessingRecord.objects.create(article=article, stage="article_viewed", metadata={"safe": True})
        except (OperationalError, ProgrammingError, DatabaseError):
            # Do not make a read endpoint unavailable while the optional
            # governance migration is being rolled out.
            pass
        return Response(ArticleDetailSerializer(article).data)


class LatestArticlesView(ListAPIView):
    serializer_class = ArticleListSerializer
    queryset = Article.objects.none()

    def get_queryset(self):
        return services.latest_articles()


class ArticleSearchView(ListAPIView):
    serializer_class = RelatedArticleSerializer

    def get_queryset(self):
        params = self.request.query_params
        query = params.get("q", "").strip()
        if not query:
            return Article.objects.none()
        return search_articles(
            query,
            mode=params.get("mode", "semantic"),
            category=params.get("category"),
            source=params.get("source"),
            date_from=params.get("date_from"),
            date_to=params.get("date_to"),
        )


class RelatedArticlesView(ListAPIView):
    serializer_class = RelatedArticleSerializer

    def get_queryset(self):
        return services.get_related(self.kwargs["pk"])


class TimelineView(APIView):
    def get(self, request, pk):
        return Response(services.get_timeline(pk))


class CategoriesView(APIView):
    def get(self, request):
        return Response(services.get_categories_with_counts())


class SaveArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        services.save_article_for_user(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk):
        services.unsave_article_for_user(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SavedArticlesListView(ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return services.list_saved_articles(self.request.user)
