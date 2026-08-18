# Deployment

Set backend secrets in the environment (`DJANGO_SECRET_KEY`, `GEMINI_API_KEY`, database settings, CORS origins). Do not commit `.env` files. Run `python manage.py migrate`, collect static files if serving Django static assets, then run behind TLS with an ASGI server/proxy that disables buffering for `/api/chat/stream/`.

React requires `VITE_API_BASE_URL` at build time. Use Redis rather than the configured local-memory cache when running multiple workers.

Readiness: Django/React are **NEEDS HARDENING**; local cache, external web providers, and deployment topology are **PROTOTYPE**.
