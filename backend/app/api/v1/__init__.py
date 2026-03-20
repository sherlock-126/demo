"""API v1 routes"""

from fastapi import APIRouter
from app.api.v1.endpoints import scripts, images, videos, events

api_router = APIRouter()

api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(events.router, prefix="/events", tags=["events"])