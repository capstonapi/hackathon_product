# Architecture

```text
React (Vite) → Django REST/SSE → controlled RAG service
                                  ├─ PostgreSQL + pgvector
                                  ├─ source-policy registry
                                  └─ Gemini / external retrieval
```

Article reads use paginated Django ORM queries. Chat uses token authentication, controlled retrievers, source-aware context merging, and SSE statuses. The model receives evidence text only through the prompt builder; it cannot run SQL or tools.

Status: frontend and core API are **READY for development**. External retrieval and Gemini remain **NEEDS HARDENING** for production scale.
