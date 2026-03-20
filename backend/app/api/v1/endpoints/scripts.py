"""Script generation endpoints"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.script import ScriptGenerationRequest, ScriptResponse
from app.services.content_service import content_service
from app.core.tasks import task_manager
from app.core.events import event_manager
from datetime import datetime

router = APIRouter()


@router.post("/generate", response_model=dict)
async def generate_script(
    request: ScriptGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate a new script from topic"""
    try:
        # Create task
        task_id = task_manager.create_task("script_generation")
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

                # Generate script
                result = await content_service.generate_script(
                    task,
                    topic=request.topic,
                    num_slides=request.num_slides,
                    language=request.language
                )

                # Send completion event
                await event_manager.send_event(
                    task_id,
                    "complete",
                    {"task_id": task_id, "result": result}
                )

            except Exception as e:
                # Send error event
                await event_manager.send_event(
                    task_id,
                    "error",
                    {"task_id": task_id, "error": str(e)}
                )
                raise

        background_tasks.add_task(run_generation)

        return {
            "task_id": task_id,
            "status": "started",
            "message": "Script generation started"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}")
async def get_script(script_id: str):
    """Get script by ID"""
    import os
    import json
    from app.core.config import settings

    script_path = os.path.join(settings.data_dir, f"{script_id}.json")

    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="Script not found")

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        return script_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))