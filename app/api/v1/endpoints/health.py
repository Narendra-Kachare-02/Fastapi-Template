"""Health check endpoint: GET api/v1/health."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health():
    return {"status": "ok"}
