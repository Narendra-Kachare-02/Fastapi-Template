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
│   │       └── endpoints/     # route handlers (health, orders, …)
│   │           ├── __init__.py
│   │           ├── health.py
│   │           └── orders.py
│   ├── services/              # business logic (e.g. order.py)
│   ├── repositories/          # data access (e.g. order.py)
│   ├── models/               # Pydantic / domain models (e.g. order.py)
│   ├── db/                    # async engine and session from config
│   │   ├── __init__.py
│   │   └── session.py
│   └── utils/                 # shared helpers (e.g. logging)
│       ├── __init__.py
│       └── logging.py
├── tests/
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
| **Models**     | `app/models/`         | Pydantic request/response and domain models. |
| **Config**     | `app/config.py`       | Load env and `.env`; expose app and DB settings. Build `DATABASE_URL` from `DB_*`. |
| **DB**         | `app/db/`             | Async SQLAlchemy engine and session factory from `DATABASE_URL`. |
| **Utils**      | `app/utils/`          | Cross-cutting helpers (e.g. centralized logging). |

## Request flow

1. **HTTP request** → FastAPI router in `app/api/v1/endpoints/`.
2. **Endpoint** validates body/path (Pydantic), calls **service**.
3. **Service** implements the use case and calls **repository**.
4. **Repository** reads/writes data (DB or in-memory).
5. **Response** flows back: repository → service → endpoint → HTTP.

Dependencies (e.g. DB session) can be injected via FastAPI’s DI; config is imported from `app.config`.

## API versioning

- All v1 routes are under **`/api/v1/`** (e.g. `/api/v1/health`, `/api/v1/orders`).
- Route modules live in `app/api/v1/endpoints/`; the v1 router is defined in `app/api/v1/__init__.py` and mounted in `app/main.py`.
- New endpoints: add a module under `endpoints/` and include its router in `app/api/v1/__init__.py`. For a future v2, add `app/api/v2/` and a separate prefix.

## Configuration and database

- **Config:** `app/config.py` loads `.env` and exposes `APP_*` and `DB_*` variables. It builds **`DATABASE_URL`** from `DB_SCHEME`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`.
- **Database:** `app/db/session.py` creates an async SQLAlchemy engine from `DATABASE_URL` and provides `async_session_factory` and `get_async_session`. Repositories use the session for persistence when connected to a real DB.

## Logging

- Configured in `app/utils/logging.py` (level from `LOG_LEVEL`). Used at app start/end, important operations (e.g. order create), and on exceptions (e.g. DB session failure, order not found).

## Naming and style

- **Domain-based file names:** e.g. `order.py` in `services/`, `repositories/`, `models/` (folder indicates the layer).
- **Snake_case** for modules and functions, **PascalCase** for classes. One main responsibility per module/class. See [RULE.md](RULE.md) for the full checklist.
