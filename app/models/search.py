"""Search API request/response models."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request body for RAG search."""

    query: str = Field(..., min_length=1, description="User question or search query")
    top_k: int | None = Field(None, ge=1, le=20, description="Max number of chunks to retrieve (default from config)")


class SnomedConcept(BaseModel):
    """A retrieved SNOMED concept reference."""

    conceptId: str | None = None
    PreferredName: str | None = None


class SearchResponse(BaseModel):
    """Response from RAG search (answer + retrieved concepts)."""

    answer: str | None = Field(None, description="LLM-generated answer (JSON string); None if LLM not configured")
    retrieved: list[SnomedConcept] = Field(default_factory=list, description="Top retrieved SNOMED concepts")
