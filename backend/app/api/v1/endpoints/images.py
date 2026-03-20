"""Image generation endpoints"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.image import ImageGenerationRequest, ImageGenerationResponse, ImageStatus
from app.services.layout_service import layout_service
from app.core.tasks import task_manager
from app.core.events import event_manager

router = APIRouter()


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_images(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate images from script"""
    try:
        # Create task
        task_id = task_manager.create_task("image_generation")
        task = task_manager.get_task(task_id)

        # Run generation in background
        async def run_generation():
            try:
                # Send start event
                await event_manager.send_event(
                    task_id,
                    "start",
                    {"task_id": task_id, "status": "started"}
                )

                # Generate images
                images = await layout_service.generate_images(
                    task,
                    script_id=request.script_id
                )

                # Update task with result
                task.metadata["images"] = images

                # Send completion event
                await event_manager.send_event(
                    task_id,
                    "complete",
                    {"task_id": task_id, "images": images}
                )

            except Exception as e:
                # Send error event
                await event_manager.send_event(
                    task_id,
                    "error",
                    {"task_id": task_id, "error": str(e)}
                )
                task.fail(str(e))

        background_tasks.add_task(run_generation)

        return ImageGenerationResponse(
            task_id=task_id,
            status="started"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}/status", response_model=ImageStatus)
async def get_image_status(task_id: str):
    """Get image generation status"""
    task = task_manager.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return ImageStatus(
        task_id=task_id,
        status=task.status,
        progress=task.progress,
        images=task.metadata.get("images", []),
        error=task.error,
        started_at=task.started_at,
        completed_at=task.completed_at
    )