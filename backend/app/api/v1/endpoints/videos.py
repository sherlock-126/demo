"""
Video generation endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional
import logging
import uuid
from pathlib import Path

from backend.app.schemas.video import VideoCreateRequest, VideoResponse
from backend.app.services.video_service import VideoService

router = APIRouter()
logger = logging.getLogger(__name__)
video_service = VideoService()

@router.post("/create", response_model=VideoResponse)
async def create_video(
    request: VideoCreateRequest,
    background_tasks: BackgroundTasks
) -> VideoResponse:
    """Create a video from images"""
    try:
        # Generate video ID
        video_id = str(uuid.uuid4())

        # Start video generation in background
        background_tasks.add_task(
            video_service.create_video_async,
            script_id=request.script_id,
            video_id=video_id,
            music_path=request.music_path,
            duration_per_slide=request.duration_per_slide
        )

        return VideoResponse(
            id=video_id,
            script_id=request.script_id,
            status="processing",
            file_path=None
        )
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}/status", response_model=VideoResponse)
async def get_video_status(video_id: str) -> VideoResponse:
    """Get video generation status"""
    try:
        status = await video_service.get_video_status(video_id)
        if not status:
            raise HTTPException(status_code=404, detail="Video not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}/download")
async def download_video(video_id: str):
    """Download a generated video"""
    try:
        video_info = await video_service.get_video_status(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="Video not found")

        if video_info["status"] != "completed":
            raise HTTPException(status_code=400, detail="Video not ready")

        file_path = Path(video_info["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Video file not found")

        return FileResponse(
            path=str(file_path),
            media_type="video/mp4",
            filename=f"video_{video_id}.mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_videos(
    skip: int = 0,
    limit: int = 10
) -> Dict[str, Any]:
    """List all videos"""
    try:
        videos = await video_service.list_videos(skip=skip, limit=limit)
        return {
            "videos": videos,
            "total": len(videos),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))