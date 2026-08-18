from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.articles.governance import assess_article, reassess_event, verified_articles
from apps.articles.models import Article
from services.claims import verify_article_claims


def article(title, source, url, content="Verified reporting has enough article text. " * 12):
    return Article.objects.create(category="world", title=title, source=source, url=url,
                                  content=content, summary=content[:200], published_at=timezone.now().isoformat())


class GovernanceAdmissionTests(TestCase):
    def test_trusted_article_without_independent_coverage_remains_pending(self):
        reuters = article("Government announces climate policy", "Reuters", "https://reuters.com/policy")

        assess_article(reuters)

        self.assertEqual(reuters.active_metadata.verification_status, "PENDING")
        self.assertEqual(verified_articles().count(), 0)

    def test_only_independently_corroborated_trusted_story_is_public(self):
        reuters = article("Government announces climate policy", "Reuters", "https://reuters.com/policy")
        bbc = article("Government announces new climate policy", "BBC", "https://bbc.com/policy")
        reassess_event(bbc)
        reuters.refresh_from_db()
        self.assertEqual(verified_articles().get().id, reuters.id)
        self.assertEqual(reuters.active_metadata.verification_status, "VERIFIED")
        self.assertEqual(bbc.active_metadata.verification_status, "DUPLICATE")

    def test_untrusted_low_quality_and_expired_articles_never_enter_public_query(self):
        untrusted = article("Same trusted looking story", "Unknown Blog", "https://blog.invalid/story")
        assess_article(untrusted)
        low_quality = article("Short story", "Reuters", "https://reuters.com/short", content="too short")
        assess_article(low_quality)
        old = article("Old story is no longer current", "Reuters", "https://reuters.com/old")
        old.published_at = (timezone.now() - timedelta(days=8)).isoformat()
        old.save(update_fields=["published_at"])
        assess_article(old)
        self.assertEqual(verified_articles().count(), 0)
        self.assertEqual(untrusted.active_metadata.verification_status, "UNTRUSTED_SOURCE")

    def test_claim_is_supported_only_by_relevant_independent_coverage(self):
        claim_text = "The government announced a climate policy today with new emissions targets."
        reuters = article("Government announces climate policy", "Reuters", "https://reuters.com/policy",
                          claim_text + " Additional reporting provides implementation detail." * 6)
        bbc = article("Government announces new climate policy", "BBC", "https://bbc.com/policy",
                      "The government announced a climate policy today with new emissions targets."
                      + " Additional reporting provides implementation detail." * 6)
        reassess_event(bbc)

        claims = list(verify_article_claims(reuters))

        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].status, "SUPPORTED")
        self.assertEqual(claims[0].evidence.count(), 1)
        self.assertEqual(claims[0].evidence.get().source, "BBC")

    def test_claim_without_matching_independent_coverage_is_insufficient_evidence(self):
        reuters = article("Government announces climate policy", "Reuters", "https://reuters.com/policy",
                          "The government announced a climate policy today with new emissions targets."
                          + " Additional reporting provides implementation detail." * 6)
        bbc = article("Government announces new climate policy", "BBC", "https://bbc.com/policy",
                      "The government announced a climate policy today. Details followed."
                      + " Additional reporting provides implementation detail." * 6)
        reassess_event(bbc)

        claims = list(verify_article_claims(reuters))

        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].status, "INSUFFICIENT_EVIDENCE")
