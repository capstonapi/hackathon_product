from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.articles.governance import assess_article, reassess_event, verified_articles
from apps.articles.models import Article


def article(title, source, url, content="Verified reporting has enough article text. " * 12):
    return Article.objects.create(category="world", title=title, source=source, url=url,
                                  content=content, summary=content[:200], published_at=timezone.now().isoformat())


class GovernanceAdmissionTests(TestCase):
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
