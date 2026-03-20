"""
Image generation endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import logging
import uuid

from backend.app.schemas.script import ImageGenerateRequest, ImageResponse
from backend.app.services.content_service import ContentService

router = APIRouter()
logger = logging.getLogger(__name__)
content_service = ContentService()

@router.post("/generate", response_model=ImageResponse)
async def generate_images(
    request: ImageGenerateRequest,
    background_tasks: BackgroundTasks
) -> ImageResponse:
    """Generate images from a script"""
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())

        # Start image generation in background
        background_tasks.add_task(
            content_service.generate_images_async,
            script_id=request.script_id,
            task_id=task_id
        )

        return ImageResponse(
            task_id=task_id,
            script_id=request.script_id,
            status="processing",
            images=[]
        )
    except Exception as e:
        logger.error(f"Error generating images: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}", response_model=ImageResponse)
async def get_image_generation_status(task_id: str) -> ImageResponse:
    """Get image generation task status"""
    try:
        status = await content_service.get_image_generation_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/{script_id}")
async def list_images(script_id: str) -> Dict[str, Any]:
    """List all images for a script"""
    try:
        images = await content_service.list_images(script_id)
        return {
            "script_id": script_id,
            "images": images,
            "total": len(images)
        }
    except Exception as e:
        logger.error(f"Error listing images: {e}")
        raise HTTPException(status_code=500, detail=str(e))