"""Pydantic models for image generation"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    script_id: str = Field(..., description="ID of the script to generate images for")


class ImageGenerationResponse(BaseModel):
    """Response model for image generation"""
    task_id: str
    status: str
    message: str = "Image generation started"


class ImageStatus(BaseModel):
    """Image generation status"""
    task_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    images: List[str] = []
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None