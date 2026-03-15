"""API package: versioned routes under api/v1/, api/v2/, etc."""

from app.api.v1 import router as v1_router

__all__ = ["v1_router"]
