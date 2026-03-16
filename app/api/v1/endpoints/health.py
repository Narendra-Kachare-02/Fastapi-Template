"""Health check endpoint: GET api/v1/health."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("")
def health():
    return {"status": "ok"}
