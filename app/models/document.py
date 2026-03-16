"""Document and ingestion API models."""

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for one document (e.g. SNOMED conceptId, PreferredName)."""

    conceptId: str | None = None
    PreferredName: str | None = None


class DocumentInput(BaseModel):
    """One document to ingest: content and optional metadata."""

    content: str = Field(..., min_length=1, description="Document text content")
    metadata: DocumentMetadata | None = Field(None, description="Optional metadata (e.g. conceptId, PreferredName)")


class IngestRequest(BaseModel):
    """Request body for ingesting documents into RAG."""

    documents: list[DocumentInput] = Field(..., min_length=1, description="List of documents to ingest")


class IngestResponse(BaseModel):
    """Response after ingestion."""

    documents_ingested: int