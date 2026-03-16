"""API v1: all v1 routes under api/v1/ (handlers in endpoints/ folder)."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, ingest, search

router = APIRouter(prefix="/api/v1")

router.include_router(health.router, prefix="/health")
router.include_router(search.router, prefix="/search")
router.include_router(ingest.router, prefix="/ingest")
