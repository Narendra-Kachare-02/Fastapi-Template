# Snomed

FastAPI sample project following the [ARCHITECTURE.md](ARCHITECTURE.md) and [RULE.md](RULE.md): domain-based structure, service/repository pattern, thin controllers, and centralized config/logging.

## Setup

Requires [uv](https://docs.astral.sh/uv/). From the project root:

```bash
uv sync
uv sync --extra dev   # for pytest
```

Copy `.env.example` to `.env` and adjust (see [Environment variables](#environment-variables) and [Database](#database)).

## Run the server

```bash
uv run python main.py
```

Then open:

- http://localhost:8000/ — root message
- http://localhost:8000/docs — Swagger UI
- http://localhost:8000/api/v1/health — health check
- http://localhost:8000/api/v1/orders — orders API
- http://localhost:8000/api/v1/search — RAG search (POST)
- http://localhost:8000/api/v1/ingest — RAG ingest (POST)

## Tests

```bash
uv run pytest tests/ -v
```

## Environment variables

| Variable      | Description       | Default       |
|---------------|-------------------|---------------|
| `APP_TITLE`   | Application title | `snomed`      |
| `APP_DEBUG`   | Enable debug mode | `false`       |
| `LOG_LEVEL`   | Logging level     | `INFO`        |
| `DB_SCHEME`   | Database type     | `postgresql`  |
| `DB_HOST`     | Database host     | `localhost`   |
| `DB_PORT`     | Database port     | `5432`        |
| `DB_USER`     | Database user     | `snomed`      |
| `DB_PASSWORD` | Database password | *(empty)*     |
| `DB_NAME`     | Database name     | `snomed`      |
| `VECTOR_DATABASE_URL` | Sync Postgres URL for pgvector | *(optional; built from DB_* if PostgreSQL)* |
| `RAG_COLLECTION_NAME` | pgvector collection name | `snomed_vectors` |
| `RAG_EMBEDDING_MODEL` | HuggingFace model | `BAAI/bge-large-en` |
| `RAG_TOP_K`   | Max chunks per search | `5` |
| `OPENAI_API_KEY` | OpenAI API key for LLM answers in search | *(empty)* |

The app builds `DATABASE_URL` from the DB_* variables in `app/config.py`. For SQLite set `DB_SCHEME=sqlite` and use `DB_NAME` as path (e.g. `./snomed.db`). For MySQL use `DB_SCHEME=mysql`, `DB_PORT=3306` and `uv add aiomysql`. RAG uses **pgvector** (PostgreSQL with the pgvector extension). If the main DB is PostgreSQL, the vector URL is built as `postgresql+psycopg://...` from DB_*; otherwise set `VECTOR_DATABASE_URL`. Set `OPENAI_API_KEY` for generated answers in search.

## Database

Config reads `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (and `DB_SCHEME`) and builds the connection URL in code. Used in `app/db/session.py`; repositories inject `get_async_session` for persistence. See `.env.example`.

**RAG / pgvector:** Vector store uses PostgreSQL with the pgvector extension. Connection string is in `app/config.py` (from DB_* or `VECTOR_DATABASE_URL`); `app/db/pgvector.py` exposes it; vector access in `app/repositories/vector.py`.

## SNOMED data preparation and ingest

To load SNOMED data from raw release files into the vector store:

1. **Prepare final TSV** from description and definition TSVs (same logic as Langchain RAG `prepare_snomed_data.py`):
   ```bash
   uv run python scripts/prepare_snomed_data.py
   ```
   Default inputs: `data/snomed_description.txt`, `data/snomed_definition.txt`. Output: `data/snomed_final.txt`. Use `--description`, `--definition`, `--output` to override.

2. **Ingest into pgvector** (Postgres with pgvector must be running; the FastAPI app does not need to be running):
   ```bash
   uv run python scripts/ingest_snomed_from_tsv.py
   ```
   Default: reads `data/snomed_final.txt`, uses 10 parallel workers. Options: `--workers 10 --batch-size 100`, `--limit 10` (test with 10 docs), `--workers 1` (single-threaded). Or pass path: `uv run python scripts/ingest_snomed_from_tsv.py /path/to/snomed_final.txt`.

## Structure (summary)

- `app/main.py` — FastAPI app and router registration
- `app/config.py` — settings from env / `.env` (DB_*, pgvector, RAG)
- `app/db/` — async engine and session; pgvector connection (`pgvector.py`)
- `app/api/v1/endpoints/` — thin route handlers (health, orders, search, ingest)
- `app/services/` — business logic (including rag, retrieval, embedding, generation, ingestion)
- `app/repositories/` — data access (vector.py for pgvector, document.py optional)
- `app/models/` — Pydantic models (search, document, rag, order)
- `app/prompts/` — prompt templates (rag, snomed, templates)
- `app/utils/` — e.g. centralized logging
- `tests/` — test suite
- `docs/` — documentation (this folder)
- `scripts/` — `prepare_snomed_data.py` (raw SNOMED TSVs → final TSV), `ingest_snomed_from_tsv.py` (final TSV → pgvector)

## API versioning

- **v1:** All endpoints under `/api/v1/`
  - `GET /api/v1/health` – health check
  - `POST /api/v1/orders` – create order
  - `GET /api/v1/orders` – list orders
  - `GET /api/v1/orders/{order_id}` – get order by id
  - `POST /api/v1/search` – RAG search (body: `query`, optional `top_k`; returns answer + retrieved SNOMED concepts)
  - `POST /api/v1/ingest` – RAG ingest (body: `documents` with `content` and optional `metadata`)

See [ARCHITECTURE.md](ARCHITECTURE.md) (architecture, including RAG and layers), [SETUP_AND_RUN.md](SETUP_AND_RUN.md) (step-by-step setup and run), and [RULE.md](RULE.md) (coding rules) for details.
