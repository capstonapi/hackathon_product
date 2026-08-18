from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.search.services import search_entities
from services.claims import get_claim_evidence

from .models import Article, ArticleMetadata, SavedArticle

User = get_user_model()


def make_article(**kwargs):
    defaults = dict(
        category="technology",
        title="Test Article",
        url=f"https://example.com/{kwargs.get('title', 'article').lower().replace(' ', '-')}",
        content="Some article content.",
        summary="A short summary.",
        source="Test Source",
        published_at="2026-01-01T00:00:00Z",
    )
    defaults.update(kwargs)
    article = Article.objects.create(**defaults)
    ArticleMetadata.objects.create(article=article, verification_status="VERIFIED", source_trust=1,
                                   quality_score=1, freshness_score=1, evidence={"corroborating_sources": []})
    return article


class ArticleListTests(APITestCase):
    def setUp(self):
        make_article(title="Tech One", category="technology")
        make_article(title="Sports One", category="sports")

    def test_list_returns_all(self):
        resp = self.client.get("/api/articles/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

    def test_list_filters_by_category(self):
        resp = self.client.get("/api/articles/?category=sports")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["title"], "Sports One")

    def test_pagination(self):
        for i in range(25):
            make_article(title=f"Extra {i}")
        resp = self.client.get("/api/articles/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 20)
        self.assertIsNotNone(resp.data["next"])
        resp2 = self.client.get(resp.data["next"])
        self.assertEqual(resp2.status_code, 200)

    def test_pagination_out_of_range_page_is_404(self):
        resp = self.client.get("/api/articles/?page=999")
        self.assertEqual(resp.status_code, 404)

    def test_list_filters_by_ui_category_key_expands_to_raw_categories(self):
        # "economy" (UI key from /api/categories/) maps to the raw GNews category "business".
        make_article(title="Business News", category="business")
        resp = self.client.get("/api/articles/?category=economy")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["title"], "Business News")

    def test_list_filters_by_raw_category_still_works(self):
        make_article(title="Raw Category Match", category="business")
        resp = self.client.get("/api/articles/?category=business")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_list_filters_by_source(self):
        make_article(title="Reuters Piece", source="Reuters")
        resp = self.client.get("/api/articles/?source=reuters")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["title"], "Reuters Piece")

    def test_list_filters_by_date_range(self):
        article = make_article(title="Dated")
        far_past = "2000-01-01T00:00:00Z"
        far_future = "2999-01-01T00:00:00Z"

        in_range = self.client.get(f"/api/articles/?date_from={far_past}&date_to={far_future}")
        self.assertIn(article.id, [a["id"] for a in in_range.data["results"]])

        out_of_range = self.client.get(f"/api/articles/?date_from={far_future}")
        self.assertNotIn(article.id, [a["id"] for a in out_of_range.data["results"]])


class ArticleDetailTests(APITestCase):
    def test_detail_found(self):
        article = make_article(title="Detail Me")
        resp = self.client.get(f"/api/articles/{article.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["title"], "Detail Me")

    def test_detail_invalid_id_is_404(self):
        resp = self.client.get("/api/articles/999999/")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("error", resp.data)

    def test_latest_orders_by_fetched_at(self):
        make_article(title="Older")
        newer = make_article(title="Newer")
        resp = self.client.get("/api/articles/latest/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["results"][0]["title"], newer.title)


class ArticleSearchTests(APITestCase):
    def test_search_without_query_returns_empty(self):
        resp = self.client.get("/api/articles/search/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 0)

    @patch("apps.search.services.generate_embedding")
    def test_search_with_results(self, mock_embed):
        mock_embed.return_value = [0.1] * 768
        make_article(title="Findable", embedding=[0.1] * 768)
        resp = self.client.get("/api/articles/search/?q=findable")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    @patch("apps.search.services.generate_embedding")
    def test_search_falls_back_to_keyword_on_embedding_failure(self, mock_embed):
        mock_embed.return_value = None
        make_article(title="Anything found without embeddings")
        resp = self.client.get("/api/articles/search/?q=anything")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_keyword_search_matches_title_without_embedding_call(self):
        make_article(title="Unique Keyword Match")
        make_article(title="Unrelated")
        resp = self.client.get("/api/articles/search/?q=Unique Keyword&mode=keyword")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertIsNone(resp.data["results"][0]["distance"])

    def test_keyword_search_resolves_ui_category_key(self):
        make_article(title="Match Business", category="business")
        resp = self.client.get("/api/articles/search/?q=Match&mode=keyword&category=economy")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_keyword_search_respects_category_and_source_filters(self):
        make_article(title="Match Sports", category="sports", source="ESPN")
        make_article(title="Match Tech", category="technology", source="Reuters")
        resp = self.client.get("/api/articles/search/?q=Match&mode=keyword&category=sports")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["title"], "Match Sports")


class RelatedAndTimelineTests(APITestCase):
    def test_related_excludes_self_and_articles_without_embeddings(self):
        anchor = make_article(title="Anchor", embedding=[0.1] * 768)
        make_article(title="Similar", embedding=[0.1] * 768)
        make_article(title="No embedding")
        resp = self.client.get(f"/api/articles/{anchor.id}/related/")
        self.assertEqual(resp.status_code, 200)
        titles = [r["title"] for r in resp.data["results"]]
        self.assertNotIn("Anchor", titles)
        self.assertIn("Similar", titles)

    def test_timeline_invalid_id_is_404(self):
        resp = self.client.get("/api/articles/999999/timeline/")
        self.assertEqual(resp.status_code, 404)


class SavedArticleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.article = make_article(title="Save Me")

    def test_unauthorized_save_rejected(self):
        resp = self.client.post(f"/api/articles/{self.article.id}/save/")
        self.assertEqual(resp.status_code, 401)

    def test_unauthorized_saved_list_rejected(self):
        resp = self.client.get("/api/saved/")
        self.assertEqual(resp.status_code, 401)

    def test_save_is_idempotent_then_appears_in_list_then_removable(self):
        self.client.force_authenticate(user=self.user)

        self.assertEqual(self.client.post(f"/api/articles/{self.article.id}/save/").status_code, 204)
        self.assertEqual(self.client.post(f"/api/articles/{self.article.id}/save/").status_code, 204)
        self.assertEqual(SavedArticle.objects.filter(user=self.user).count(), 1)

        listed = self.client.get("/api/saved/")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data["count"], 1)

        removed = self.client.delete(f"/api/articles/{self.article.id}/save/")
        self.assertEqual(removed.status_code, 204)
        self.assertEqual(SavedArticle.objects.filter(user=self.user).count(), 0)

    def test_save_invalid_article_id_is_404(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/articles/999999/save/")
        self.assertEqual(resp.status_code, 404)


class CategoriesAndSourcesTests(APITestCase):
    def test_categories_public_and_counted(self):
        make_article(category="business")
        resp = self.client.get("/api/categories/")
        self.assertEqual(resp.status_code, 200)
        economy = next(c for c in resp.data if c["key"] == "economy")
        self.assertEqual(economy["count"], 1)

    def test_sources_public(self):
        make_article(source="Reuters")
        resp = self.client.get("/api/sources/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(row["source"] == "Reuters" for row in resp.data))


class ControlledToolFunctionTests(TestCase):
    """search_entities()/get_claim_evidence() are the controlled tool functions
    called instead of ever letting an LLM/agent build its own SQL."""

    def test_search_entities_finds_by_entity_text(self):
        make_article(title="Has Entity", entities=[{"text": "NASA", "label": "ORG"}])
        make_article(title="No Match", entities=[{"text": "Someone Else", "label": "PERSON"}])
        make_article(title="Null Entities", entities=None)

        results = search_entities("nasa")

        self.assertEqual([a.title for a in results], ["Has Entity"])

    def test_get_claim_evidence_rejects_unknown_claim(self):
        from apps.articles.models import Claim
        claim = Claim.objects.create(article=make_article(title="Claim article"), text="A claim")
        evidence = get_claim_evidence(claim.id)
        self.assertEqual(evidence["claim"], "A claim")
        self.assertEqual(evidence["status"], "INSUFFICIENT_EVIDENCE")
