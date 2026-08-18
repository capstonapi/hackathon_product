# Data governance

The application is in verified-only mode. Public articles, search results, related stories, saved items, and chat evidence are all derived from the `VERIFIED` ArticleMetadata queryset. A record is admitted only when it has usable extracted text, is within the seven-day freshness window, comes from a high-trust source, and is independently corroborated by a second high-trust source. Near-duplicates are retained as evidence but only the canonical article is displayed.

`SourceRegistry` is seeded by migration with Reuters, Associated Press, BBC, NASA, The Guardian, and NPR. Operators can refine this registry in Django admin; an unknown source is never admitted by default. `ProcessingRecord` preserves each governance assessment and ArticleMetadata retains the evidence links and scores used to make that decision.

Claims without matching independent evidence remain `INSUFFICIENT_EVIDENCE` and are visibly labelled as such; only supported claims are treated as confirmed. Users can erase their own account using `DELETE /api/auth/account/`, which cascades to saved articles, conversations, and messages. See `data-governance-proof-pack.md` for the review checklist and test commands.
