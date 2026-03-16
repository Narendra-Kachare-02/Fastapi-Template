"""Embedding service: convert text to vectors (HuggingFace model)."""

from typing import Any

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import RAG_EMBEDDING_MODEL
from app.utils.logging import get_logger

logger = get_logger(__name__)

_embedding_model: Any = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Return the shared HuggingFace embedding model (lazy-loaded)."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=RAG_EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("RAG embedding model loaded: %s", RAG_EMBEDDING_MODEL)
    return _embedding_model
