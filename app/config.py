"""Global settings: load from environment and .env."""

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Load .env from project root (parent of app/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


def get_env(key: str, default: str = "") -> str:
    """Return environment variable value with optional default."""
    return os.environ.get(key, default).strip()


# Application
APP_TITLE: str = get_env("APP_TITLE", "snomed")
APP_DEBUG: bool = get_env("APP_DEBUG", "false").lower() in ("1", "true", "yes")
LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO")

# Database: host, port, user, password, name — URL built in config
DB_HOST: str = get_env("DB_HOST", "localhost")
DB_PORT: str = get_env("DB_PORT", "5432")
DB_USER: str = get_env("DB_USER", "snomed")
DB_PASSWORD: str = get_env("DB_PASSWORD", "")
DB_NAME: str = get_env("DB_NAME", "snomed")

_DRIVERS = {"postgresql": "asyncpg", "mysql": "aiomysql", "sqlite": "aiosqlite"}
DB_SCHEME: str = get_env("DB_SCHEME", "postgresql").lower()
_DRIVER = _DRIVERS.get(DB_SCHEME, "asyncpg")


def _build_database_url() -> str:
    if DB_SCHEME == "sqlite":
        return f"sqlite+aiosqlite:///{DB_NAME.lstrip('/')}"
    port = f":{DB_PORT}" if DB_PORT else ""
    user_pass = f"{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@" if DB_USER else ""
    return f"{DB_SCHEME}+{_DRIVER}://{user_pass}{DB_HOST}{port}/{DB_NAME}"


DATABASE_URL: str = _build_database_url()
