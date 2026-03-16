# Snomed RAG – Setup and run

Step-by-step guide to run the app, prepare SNOMED data, ingest, and query.

## Prerequisites

- **Python 3.14** (see `.python-version`)
- **uv** – [Install uv](https://docs.astral.sh/uv/)
- **PostgreSQL** with **pgvector** (local or Docker)
- **(Optional)** **OPENAI_API_KEY** for LLM answers in search

---

## Step 1: Install dependencies

From the project root:

```bash
uv sync
```

---

## Step 2: Configure environment

```bash
cp .env.example .env
```

Edit `.env`: set PostgreSQL vars (`DB_SCHEME=postgresql`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`). If the app uses a different DB, set `VECTOR_DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname`. Optionally set `OPENAI_API_KEY` for LLM answers.

---

## Step 3: Start PostgreSQL with pgvector

Example with Docker:

```bash
docker run -e POSTGRES_USER=snomed -e POSTGRES_PASSWORD=snomed -e POSTGRES_DB=snomed -p 5432:5432 -d pgvector/pgvector:pg16
```

Use matching values in `.env`.

---

## Step 4: Run the application

```bash
uv run python main.py
```

Endpoints: http://localhost:8000/ , http://localhost:8000/docs , http://localhost:8000/api/v1/health , http://localhost:8000/api/v1/ingest , http://localhost:8000/api/v1/search .

---

## Step 5: Prepare SNOMED final TSV (from raw release files)

Place raw SNOMED TSVs in `data/` (e.g. `snomed_description.txt`, `snomed_definition.txt`). Then:

```bash
uv run python scripts/prepare_snomed_data.py
```

- **Inputs (default):** `data/snomed_description.txt`, `data/snomed_definition.txt`
- **Output (default):** `data/snomed_final.txt`

Custom paths:

```bash
uv run python scripts/prepare_snomed_data.py \
  --description data/snomed_description.txt \
  --definition data/snomed_definition.txt \
  --output data/snomed_final.txt
```

---

## Step 6: Ingest into pgvector

**Option A – From final TSV (script):**

```bash
uv run python scripts/ingest_snomed_from_tsv.py
```

Default: reads `data/snomed_final.txt`, uses **10 parallel workers** (each embeds a batch and writes to pgvector; main thread waits for all to finish). Options:

```bash
uv run python scripts/ingest_snomed_from_tsv.py /path/to/snomed_final.txt
uv run python scripts/ingest_snomed_from_tsv.py --workers 10 --batch-size 100   # 10 workers, 100 docs per batch
uv run python scripts/ingest_snomed_from_tsv.py --workers 10 --batch-size 10   # small batches: 10 docs per batch
uv run python scripts/ingest_snomed_from_tsv.py --workers 1                      # single-threaded (no parallelism)
uv run python scripts/ingest_snomed_from_tsv.py --limit 10                      # test with 10 docs only
```

**Option B – Via API (JSON):** Use `POST /api/v1/ingest` in Swagger with a `documents` array (each with `content` and optional `metadata`).

---

## Step 7: Query (search)

**Swagger:** `POST /api/v1/search` with body e.g. `{"query": "My left knee is swollen. What could it be?", "top_k": 5}`.

**curl:**

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "My left knee is swollen. What could it be?", "top_k": 5}'
```

Response includes `retrieved` (SNOMED concepts) and `answer` (if `OPENAI_API_KEY` is set).

---

## Quick reference

| Step | Command |
|------|---------|
| Install | `uv sync` |
| Config | Copy `.env.example` → `.env`, set DB (and optional `OPENAI_API_KEY`) |
| Start DB | Docker or existing Postgres with pgvector |
| Run app | `uv run python main.py` |
| Prepare final TSV | `uv run python scripts/prepare_snomed_data.py` [optional args] |
| Ingest | `uv run python scripts/ingest_snomed_from_tsv.py` [path] or `POST /api/v1/ingest` |
| Search | `POST /api/v1/search` with `{"query": \"...\", \"top_k\": 5}` |

---

## Troubleshooting

| Issue | Check |
|-------|--------|
| "Vector store requires PostgreSQL" | Set `DB_*` for Postgres or `VECTOR_DATABASE_URL` in `.env`. |
| "OPENAI_API_KEY not set" | Only needed for `answer` in search; `retrieved` works without it. |
| Description/definition file not found | Put raw TSVs in `data/` or pass `--description` / `--definition`. |
| TSV not found (ingest script) | Run from project root or pass full path to `ingest_snomed_from_tsv.py`. |
| "too many clients already" (Postgres) | Ingest uses a single shared store; if you still hit limits, lower `--workers` (e.g. `--workers 4`) or increase Postgres `max_connections`. |

---

## Reset dataset (clear embeddings)

To clear ingested documents and re-run ingest from scratch (e.g. after a failed run):

```sql
-- Clear embeddings for snomed_vectors (keep collection)
DELETE FROM langchain_pg_embedding
WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = 'snomed_vectors');
```

Or remove the collection and its embeddings:

```sql
DELETE FROM langchain_pg_embedding
WHERE collection_id IN (SELECT uuid FROM langchain_pg_collection WHERE name = 'snomed_vectors');
DELETE FROM langchain_pg_collection WHERE name = 'snomed_vectors';
```

Run in `psql` or any Postgres client connected to the same DB as in `.env`.
