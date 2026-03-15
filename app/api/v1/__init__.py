"""API v1: all v1 routes under api/v1/ (handlers in endpoints/ folder)."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, orders

router = APIRouter(prefix="/api/v1", tags=["v1"])

router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(orders.router, prefix="/orders", tags=["orders"])
