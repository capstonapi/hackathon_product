# Verified-news data governance and proof pack

## Product rule

**Only `VERIFIED` canonical articles can appear in the feed, search, related-news results, saved list, article detail, or chat evidence.** A trusted outlet alone is not enough: the event must have a second independent trusted source. The later near-duplicate is retained as corroborating evidence but does not clutter the feed.

## Controls and implementation evidence

| Requirement | Enforced control | Evidence to inspect |
| --- | --- | --- |
| Source trust | Seeded `SourceRegistry`; unknown/low-trust sources receive `UNTRUSTED_SOURCE`. | `0004_enforced_governance.py`, `source_policy.py` |
| Fact/claim checking | Independent trusted coverage is required for article verification. Claims are only `SUPPORTED` when their text overlaps corroborating coverage; all others stay `INSUFFICIENT_EVIDENCE`. | `governance.py`, `services/claims.py`, article Claim verification panel |
| Near duplicates | Similar titles are clustered. The earliest record is canonical; others get `DUPLICATE`, with source URLs retained in the canonical record's evidence. | `governance.reassess_event()` |
| Freshness | Articles older than `ARTICLE_FRESHNESS_DAYS` (default 7) become `EXPIRED` and are excluded. | `governance.article_age()` |
| Extraction quality | Text under 200 characters is `LOW_QUALITY` and excluded. | `governance.assess_article()` |
| User-data protection | Saved items and chat records are scoped by authenticated user. `DELETE /api/auth/account/` deletes the account and Django cascades its tokens, saved articles, conversations, and messages. | `users/views.py`, account control in header |

## Audit trail

Each ingest writes `ArticleMetadata` (quality/freshness/trust/status/evidence) and an append-only `ProcessingRecord` with stage `governance_assessed`. The article page shows its source trust score and linked independent corroborating sources, so a reviewer can see why it was admitted.

## Verification commands

Run these from `backend` after configuring the database:

```bash
python manage.py migrate
python manage.py test apps.articles.test_governance apps.articles.tests apps.users.tests
```

The governance tests prove that a corroborated Reuters/BBC event exposes only one verified canonical item, while unknown-source, short/broken, and expired articles are absent from the public query.
