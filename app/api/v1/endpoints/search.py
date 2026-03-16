"""Search endpoint: RAG search (retrieve + optional LLM generation)."""

from fastapi import APIRouter, HTTPException

from app.models.search import SearchRequest, SearchResponse, SnomedConcept
from app.services import rag as rag_service

router = APIRouter(tags=["search"])


@router.post("/", response_model=SearchResponse)
def search(body: SearchRequest) -> SearchResponse:
    """Run RAG: retrieve relevant SNOMED concepts and optionally generate LLM answer."""
    try:
        result = rag_service.search(query=body.query, top_k=body.top_k)
        return SearchResponse(
            answer=result.get("answer"),
            retrieved=[SnomedConcept(**c) for c in result.get("retrieved", [])],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e!s}") from e
