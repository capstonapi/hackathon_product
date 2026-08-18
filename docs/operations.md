# Operations and automated governance

The public feed is deliberately restricted to `VERIFIED` records. The backend
keeps rejected and untrusted records for lineage, but never returns them from
article, search, saved, timeline, or retrieval endpoints.

## Automated jobs

Run the following through the production scheduler. `refresh_news` ingests
current headlines and then reassesses both current and historical records.

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod python backend/manage.py refresh_news --max-per-category 5 --skip-insights
```

Schedule it every six hours on the GNews free tier; this consumes 24 category
requests a day. The job is idempotent because existing article URLs are
skipped. Do not run overlapping jobs.

## Audit and lineage

`AuditEvent` records every mutating API request with its request ID, actor (if
authenticated), route, HTTP status, and timestamp. It intentionally excludes
passwords, tokens, questions, and article contents. `ProcessingRecord` stores
per-article ingest, extraction, summary, embedding, and governance stages.

## Production baseline

Set `DJANGO_SETTINGS_MODULE=config.settings.prod` and provide all of:

```text
DJANGO_SECRET_KEY
DJANGO_ALLOWED_HOSTS
DJANGO_CORS_ALLOWED_ORIGINS
REDIS_URL
POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
GNEWS_API_KEY, GEMINI_API_KEY
```

Terminate TLS at the load balancer/reverse proxy, run database backups, and
test restoring them regularly. Define a retention period before adding any
automated deletion or archival job.
