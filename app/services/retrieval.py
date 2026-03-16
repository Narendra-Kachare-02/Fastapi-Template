"""Retrieval service: get relevant document chunks from vector store."""

from langchain_core.documents import Document

from app.config import RAG_TOP_K
from app.repositories import vector as vector_repository
from app.services.embedding import get_embedding_model
from app.utils.logging import get_logger

logger = get_logger(__name__)


def retrieve(query: str, top_k: int | None = None) -> list[Document]:
    """Return top-k most relevant documents for the query."""
    k = top_k if top_k is not None else RAG_TOP_K
    embedding = get_embedding_model()
    store = vector_repository.get_vector_store(embedding)
    retriever = store.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)
    logger.info("Retrieved %s documents for query", len(docs))
    return docs
