"""API v1 Router - aggregates all API endpoints."""

from fastapi import APIRouter

from app.api.v1.companies import router as companies_router
from app.api.v1.scores import router as scores_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

# Include sub-routers
api_router.include_router(companies_router)
api_router.include_router(scores_router)
api_router.include_router(admin_router)


@api_router.get("/ping")
async def ping() -> dict:
    """Simple ping endpoint for testing."""
    return {"message": "pong"}

