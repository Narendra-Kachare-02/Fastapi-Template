"""RAG-specific Pydantic models (legacy/compat). Use search and document models for new code."""

from pydantic import BaseModel, Field


class SnomedConceptRef(BaseModel):
    """Reference to a SNOMED concept in RAG output."""

    conceptId: str | None = None
    PreferredName: str | None = None
