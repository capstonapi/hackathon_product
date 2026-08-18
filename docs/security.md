# Security review

- Token auth protects chat, saved items, and history; conversation queries are user-scoped.
- User-facing data access uses fixed Django ORM/controlled functions; no LLM SQL execution exists.
- API keys are backend environment variables and are never sent to React.
- CORS is allowlisted by environment; CSRF middleware remains active for session use.
- A local-cache rate limit protects `/api/` endpoints. Replace it with gateway or Redis limits in multi-worker production.
- External URLs are displayed as links only; retrieved content is treated as untrusted prompt data.

**Needs hardening:** production TLS settings, Redis rate limits/cache, secret rotation, CSP, outbound URL allowlists, and security scanning.
