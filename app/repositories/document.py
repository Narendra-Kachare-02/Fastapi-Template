"""Document repository: in-memory or DB storage for document metadata (optional)."""

from typing import Any

# Placeholder for future document metadata persistence (e.g. conceptId, source path).
# Vector store holds the actual embeddings; this layer can track what was ingested.
_document_meta: dict[str, Any] = {}


def save_document_meta(doc_id: str, meta: dict[str, Any]) -> None:
    """Store document metadata by id."""
    _document_meta[doc_id] = meta


def get_document_meta(doc_id: str) -> dict[str, Any] | None:
    """Return document metadata by id or None."""
    return _document_meta.get(doc_id)


def list_document_meta() -> list[dict[str, Any]]:
    """Return all stored document metadata."""
    return list(_document_meta.values())
