"""Video assembly endpoints"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.video import VideoCreateRequest, VideoCreateResponse, VideoStatus
from app.services.video_service import video_service
from app.core.tasks import task_manager
from app.core.events import event_manager

router = APIRouter()


@router.post("/create", response_model=VideoCreateResponse)
async def create_video(
    request: VideoCreateRequest,
    background_tasks: BackgroundTasks
):
    """Create video from images"""
    try:
        # Create task
        task_id = task_manager.create_task("video_assembly")
        task = task_manager.get_task(task_id)

        # Run assembly in background
        async def run_assembly():
            try:
                # Send start event
                await event_manager.send_event(
                    task_id,
                    "start",
                    {"task_id": task_id, "status": "started"}
                )

                # Create video
                video_path = await video_service.create_video(
                    task,
                    image_paths=request.image_paths,
                    music_path=request.music_path,
                    duration_per_slide=request.duration_per_slide,
                    transition_duration=request.transition_duration
                )

                # Update task with result
                task.metadata["video_path"] = video_path

                # Send completion event
                await event_manager.send_event(
                    task_id,
                    "complete",
                    {"task_id": task_id, "video_path": video_path}
                )

            except Exception as e:
                # Send error event
                await event_manager.send_event(
                    task_id,
                    "error",
                    {"task_id": task_id, "error": str(e)}
                )
                task.fail(str(e))

        background_tasks.add_task(run_assembly)

        return VideoCreateResponse(
            task_id=task_id,
            status="started"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}/status", response_model=VideoStatus)
async def get_video_status(task_id: str):
    """Get video assembly status"""
    task = task_manager.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return VideoStatus(
        task_id=task_id,
        status=task.status,
        progress=task.progress,
        video_path=task.metadata.get("video_path"),
        error=task.error,
        started_at=task.started_at,
        completed_at=task.completed_at
    )