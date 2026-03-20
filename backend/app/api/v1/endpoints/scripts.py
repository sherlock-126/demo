"""
Script generation endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging
import uuid
from pathlib import Path

from backend.app.schemas.script import ScriptCreate, ScriptResponse
from backend.app.services.content_service import ContentService

router = APIRouter()
logger = logging.getLogger(__name__)
content_service = ContentService()

@router.post("/generate", response_model=ScriptResponse)
async def generate_script(
    script_data: ScriptCreate,
    background_tasks: BackgroundTasks
) -> ScriptResponse:
    """Generate a new script from a topic"""
    try:
        # Generate script ID
        script_id = str(uuid.uuid4())

        # Generate script using content service
        script = await content_service.generate_script(
            topic=script_data.topic,
            style=script_data.style,
            num_slides=script_data.num_slides
        )

        # Save script to file system
        script_path = Path(f"/app/data/scripts/{script_id}.json")
        script_path.parent.mkdir(parents=True, exist_ok=True)

        # Return response
        return ScriptResponse(
            id=script_id,
            topic=script_data.topic,
            content=script,
            status="completed"
        )
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: str) -> ScriptResponse:
    """Get a script by ID"""
    try:
        script = await content_service.get_script(script_id)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        return script
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_scripts(
    skip: int = 0,
    limit: int = 10
) -> Dict[str, Any]:
    """List all scripts"""
    try:
        scripts = await content_service.list_scripts(skip=skip, limit=limit)
        return {
            "scripts": scripts,
            "total": len(scripts),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing scripts: {e}")
        raise HTTPException(status_code=500, detail=str(e))