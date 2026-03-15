"""FastAPI application entry: create app and register routers."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import v1_router
from app.config import APP_DEBUG, APP_TITLE
from app.utils.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: startup and shutdown."""
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


app = FastAPI(title=APP_TITLE, debug=APP_DEBUG, lifespan=lifespan)

app.include_router(v1_router)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Hello from snomed!"}
