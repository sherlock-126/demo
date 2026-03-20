"""
API v1 router configuration
"""
from fastapi import APIRouter

from backend.app.api.v1.endpoints import scripts, images, videos

api_router = APIRouter()

api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])