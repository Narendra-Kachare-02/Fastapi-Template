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

The app builds `DATABASE_URL` from these in `app/config.py`. For SQLite set `DB_SCHEME=sqlite` and use `DB_NAME` as path (e.g. `./snomed.db`). For MySQL use `DB_SCHEME=mysql`, `DB_PORT=3306` and `uv add aiomysql`.

## Database

Config reads `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (and `DB_SCHEME`) and builds the connection URL in code. Used in `app/db/session.py`; repositories inject `get_async_session` for persistence. See `.env.example`.

## Structure (summary)

- `app/main.py` — FastAPI app and router registration
- `app/config.py` — settings from env / `.env` (DB_* → DATABASE_URL)
- `app/db/` — async engine and session from config; use in repositories
- `app/api/v1/endpoints/` — thin route handlers (health, orders)
- `app/services/` — business logic
- `app/repositories/` — data access
- `app/models/` — Pydantic models
- `app/utils/` — e.g. centralized logging
- `tests/` — test suite
- `docs/` — documentation (this folder)

## API versioning

- **v1:** All endpoints under `/api/v1/`
  - `GET /api/v1/health` – health check
  - `POST /api/v1/orders` – create order
  - `GET /api/v1/orders` – list orders
  - `GET /api/v1/orders/{order_id}` – get order by id

See [ARCHITECTURE.md](ARCHITECTURE.md) (architecture) and [RULE.md](RULE.md) (coding rules) for details.
