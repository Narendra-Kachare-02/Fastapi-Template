# Architecture

This document describes the Snomed application architecture: layout, layers, request flow, and main components. Coding rules and checklist are in [RULE.md](RULE.md).

## Overview

Snomed is a FastAPI application with a layered structure: API (thin controllers) → services (business logic) → repositories (data access). Configuration and database connection are centralized; logging is configured in one place.

## Folder structure

```
snomed/
├── app/                      # main package
│   ├── __init__.py
│   ├── config.py             # env and DB_* → DATABASE_URL
│   ├── main.py               # FastAPI app, router registration, lifespan
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py    # router prefix /api/v1
│   │       └── endpoints/     # route handlers (health, RAG)
│   │           ├── __init__.py
│   │           ├── health.py
│   │           ├── search.py     # RAG search
│   │           └── ingest.py     # RAG ingest
│   ├── services/              # business logic
│   │   ├── rag.py            # RAG pipeline
│   │   ├── retrieval.py      # vector search logic
│   │   ├── embedding.py      # embedding model
│   │   ├── generation.py     # LLM call
│   │   └── ingestion.py      # store docs
│   ├── repositories/          # data access
│   │   ├── vector.py         # pgvector
│   │   └── document.py       # document metadata (optional)
│   ├── models/               # Pydantic / domain models
│   │   ├── search.py
│   │   ├── document.py
│   │   └── rag.py
│   ├── prompts/              # prompt templates only (no helper logic)
│   │   ├── rag.py
│   │   └── snomed.py
│   ├── db/                    # connection only
│   │   ├── session.py
│   │   └── pgvector.py        # pgvector connection string
│   └── utils/                 # shared helpers (e.g. logging)
│       ├── __init__.py
│       └── logging.py
├── tests/
├── scripts/                   # CLI scripts (SNOMED data prep and ingest)
│   ├── prepare_snomed_data.py # raw TSVs → final TSV (data/snomed_final.txt)
│   └── ingest_snomed_from_tsv.py  # final TSV → pgvector
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md        # this file
│   └── RULE.md               # coding rules and checklist
├── main.py                    # entry: uvicorn app.main:app
├── .env / .env.example
└── pyproject.toml
```

## Layers

| Layer          | Location              | Responsibility |
|----------------|-----------------------|----------------|
| **Entry**      | `main.py`             | Run uvicorn with `app.main:app`. |
| **App**        | `app/main.py`         | Create FastAPI app, register routers, lifespan. |
| **API**        | `app/api/v1/endpoints/`| Thin controllers: validate input, call service, return response. No business or DB logic. |
| **Services**   | `app/services/`       | Business logic and use cases. Call repositories. |
| **Repositories** | `app/repositories/`| Data access (DB, in-memory, or other backends). |
| **Models**     | `app/models/`         | Pydantic request/response and domain models (search, document, rag). |
| **Prompts**    | `app/prompts/`        | Prompt templates only (no helper logic; e.g. `rag.py`, `snomed.py`). |
| **Config**     | `app/config.py`       | Load env and `.env`; expose app, DB, and RAG (pgvector, embedding, LLM) settings. |
| **DB**         | `app/db/`             | Async SQLAlchemy session; pgvector connection (sync URL for Langchain). |
| **Utils**      | `app/utils/`          | Cross-cutting helpers (e.g. centralized logging, prompt helpers). |

## Request flow

1. **HTTP request** → FastAPI router in `app/api/v1/endpoints/`.
2. **Endpoint** validates body/path (Pydantic), calls **service**.
3. **Service** implements the use case and calls **repository**.
4. **Repository** reads/writes data (DB or in-memory).
5. **Response** flows back: repository → service → endpoint → HTTP.

Dependencies (e.g. DB session) can be injected via FastAPI’s DI; config is imported from `app.config`.

## API versioning

- All v1 routes are under **`/api/v1/`** (e.g. `/api/v1/health`, `/api/v1/search`, `/api/v1/ingest`).
- Route modules live in `app/api/v1/endpoints/`; the v1 router is defined in `app/api/v1/__init__.py` and mounted in `app/main.py`.
- New endpoints: add a module under `endpoints/` and include its router in `app/api/v1/__init__.py`. For a future v2, add `app/api/v2/` and a separate prefix.

## Configuration and database

- **Config:** `app/config.py` loads `.env` and exposes `APP_*` and `DB_*` variables. It builds **`DATABASE_URL`** from `DB_SCHEME`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`. For RAG it also builds **`VECTOR_DATABASE_URL`** (sync `postgresql+psycopg://` URL) from the same DB_* when `DB_SCHEME` is `postgresql`, or from env `VECTOR_DATABASE_URL` if set.
- **Database:** `app/db/session.py` creates an async SQLAlchemy engine from `DATABASE_URL` and provides `async_session_factory` and `get_async_session`. Repositories use the session for persistence when connected to a real DB. **pgvector:** Vector store uses PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension; connection string is provided by `app/db/pgvector.py` (sync URL for Langchain PGVector).

## Logging

- Configured in `app/utils/logging.py` (level from `LOG_LEVEL`). Used at app start/end, important operations (e.g. order create), and on exceptions (e.g. DB session failure, order not found).

## Naming and style

- **Domain-based file names:** e.g. `order.py` in `services/`, `repositories/`, `models/` (folder indicates the layer).
- **Snake_case** for modules and functions, **PascalCase** for classes. One main responsibility per module/class. See [RULE.md](RULE.md) for the full checklist.

## RAG and layers

RAG features follow the same layers; no extra top-level RAG folder.

| RAG part        | Layer        | Location |
|-----------------|-------------|----------|
| Embedding       | Service     | `services/embedding.py` |
| Retrieval       | Service     | `services/retrieval.py` |
| Generation      | Service     | `services/generation.py` |
| Pipeline        | Service     | `services/rag.py` |
| Ingestion       | Service     | `services/ingestion.py` |
| Vector DB       | Repository  | `repositories/vector.py` |
| Document meta   | Repository  | `repositories/document.py` |
| Prompt template | Prompts     | `prompts/rag.py`, `prompts/snomed.py` |
| Endpoints       | API         | `api/v1/endpoints/search.py`, `ingest.py` |
| DB client       | DB          | `db/pgvector.py` |
