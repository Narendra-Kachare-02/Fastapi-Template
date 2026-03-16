"""Ingest endpoint: upload documents into RAG vector store."""

from fastapi import APIRouter, HTTPException
from langchain_core.documents import Document

from app.models.document import IngestRequest, IngestResponse
from app.services import ingestion as ingestion_service

router = APIRouter(tags=["ingest"])


@router.post("/", response_model=IngestResponse)
def ingest(body: IngestRequest) -> IngestResponse:
    """Ingest documents into Qdrant (embed and store)."""
    try:
        documents = [
            Document(
                page_content=d.content,
                metadata=d.metadata.model_dump(exclude_none=True) if d.metadata else {},
            )
            for d in body.documents
        ]
        count = ingestion_service.ingest_documents(documents=documents)
        return IngestResponse(documents_ingested=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {e!s}") from e
