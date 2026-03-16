"""pgvector connection: sync URL for Langchain PGVector. Used by vector repository."""

from app.config import VECTOR_DATABASE_URL
from app.utils.logging import get_logger

logger = get_logger(__name__)


def get_vector_connection_string() -> str:
    """Return the sync PostgreSQL connection string for pgvector (postgresql+psycopg://)."""
    return VECTOR_DATABASE_URL
