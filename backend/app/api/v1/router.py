from fastapi import APIRouter

from app.api.v1 import trends
from app.api.v1 import clusters, daily_brief, dashboard, stories

api_router = APIRouter()
api_router.include_router(dashboard.router)
api_router.include_router(stories.router)
api_router.include_router(clusters.router)
api_router.include_router(trends.router)
api_router.include_router(daily_brief.router)
