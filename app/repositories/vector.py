"""Vector store repository: pgvector data access (search, add documents)."""

from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector, DistanceStrategy

from app.config import RAG_COLLECTION_NAME
from app.db.pgvector import get_vector_connection_string
from app.utils.logging import get_logger

logger = get_logger(__name__)


def get_vector_store(embedding):  # noqa: ANN001
    """Return a Langchain PGVector store for the configured collection."""
    connection = get_vector_connection_string()
    if not connection:
        raise ValueError(
            "Vector store requires PostgreSQL. Set DB_* for PostgreSQL or set VECTOR_DATABASE_URL (postgresql+psycopg://...)."
        )
    return PGVector(
        connection=connection,
        collection_name=RAG_COLLECTION_NAME,
        embeddings=embedding,
        distance_strategy=DistanceStrategy.COSINE,
        use_jsonb=True,
        create_extension=True,
    )


def create_collection_from_documents(documents: list[Document], embedding) -> None:  # noqa: ANN001
    """Create pgvector collection/tables and add documents (used on first ingest)."""
    store = get_vector_store(embedding)
    store.add_documents(documents=documents)
    logger.info("Vector store created from %s documents", len(documents))


def add_documents_to_store(documents: list[Document], embedding) -> None:  # noqa: ANN001
    """Add documents to existing vector store."""
    store = get_vector_store(embedding)
    store.add_documents(documents=documents)
    logger.info("Added %s documents to vector store", len(documents))


def ensure_collection_exists(embedding) -> None:  # noqa: ANN001
    """Ensure pgvector collection and tables exist (no documents added)."""
    get_vector_store(embedding)


def add_embeddings_to_store(
    texts: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
    embedding,  # noqa: ANN001
    ids: list[str] | None = None,
) -> list[str]:
    """Add precomputed embeddings to the vector store. Returns list of document ids."""
    store = get_vector_store(embedding)
    return store.add_embeddings(
        texts=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
