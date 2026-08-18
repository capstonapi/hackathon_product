# Briefly frontend

React, TypeScript, Vite, React Router, TanStack Query, Axios, and Tailwind power the news-product UI. It consumes the Django REST API only; retrieval, AI, and article processing stay in Django.

## Run

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_BASE_URL` to the API root (for example `http://localhost:8000/api`). Start Django separately. Production validation is available through `npm run build` and `npm run lint`.

## Routes

`/`, `/latest`, `/library`, `/search`, `/saved`, `/history`, `/article/:id`, and `/article/:id/chat`.

## API integrations

The screens use `/articles/`, `/articles/latest/`, `/articles/search/`, article detail/related/timeline endpoints, `/categories/`, `/sources/`, `/saved/`, `/history/`, and `/chat/`. Auth tokens are attached by the shared Axios client.

## Current limitations

- Django currently exposes a request/response chat endpoint, rather than SSE/WebSocket tokens. The UI provides retrieval-status updates and progressively renders the completed response; true token streaming requires a streaming backend endpoint.
- The current Django article-list API supports category, source, and date filters. It does not expose an active/archived field, so that filter cannot be shown truthfully yet.
- Saved articles and conversation history require the existing token-based authentication flow; sign-in/register screens are not part of this phase.
- Vitest 4 in the committed dependency tree requires a newer Node runtime than this workspace (it imports `node:util.styleText`). The production build and lint pass; upgrade Node or align Vitest before executing browser tests.
