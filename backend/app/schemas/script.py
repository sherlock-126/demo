"""
Script-related Pydantic models
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class ScriptCreate(BaseModel):
    """Request model for script creation"""
    topic: str
    style: Optional[str] = "parenting"
    num_slides: Optional[int] = 5

class ScriptResponse(BaseModel):
    """Response model for script data"""
    id: str
    topic: str
    content: Dict[str, Any]
    status: str
    created_at: Optional[datetime] = None

class ImageGenerateRequest(BaseModel):
    """Request model for image generation"""
    script_id: str
    style: Optional[str] = "split-screen"

class ImageResponse(BaseModel):
    """Response model for image generation"""
    task_id: str
    script_id: str
    status: str
    images: List[str]
    created_at: Optional[datetime] = None