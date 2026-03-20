"""Pydantic models for video assembly"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class VideoCreateRequest(BaseModel):
    """Request model for video creation"""
    image_paths: List[str] = Field(..., min_items=1, description="List of image paths")
    music_path: Optional[str] = Field(default=None, description="Background music path")
    duration_per_slide: float = Field(default=3.0, gt=0, le=10, description="Duration per slide in seconds")
    transition_duration: float = Field(default=0.5, ge=0, le=2, description="Transition duration in seconds")


class VideoCreateResponse(BaseModel):
    """Response model for video creation"""
    task_id: str
    status: str
    message: str = "Video assembly started"


class VideoStatus(BaseModel):
    """Video assembly status"""
    task_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    video_path: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None