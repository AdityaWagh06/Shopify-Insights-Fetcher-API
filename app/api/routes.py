from fastapi import APIRouter

from app.api.v1.endpoints import insights, health

api_router = APIRouter()

# Include API endpoints
api_router.include_router(insights.router, tags=["insights"])
api_router.include_router(health.router, tags=["health"])