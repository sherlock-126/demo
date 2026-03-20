"""
Video-related Pydantic models
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoCreateRequest(BaseModel):
    """Request model for video creation"""
    script_id: str
    music_path: Optional[str] = None
    duration_per_slide: Optional[float] = 3.0
    transition_duration: Optional[float] = 0.5

class VideoResponse(BaseModel):
    """Response model for video data"""
    id: str
    script_id: str
    status: str
    file_path: Optional[str] = None
    duration: Optional[float] = None
    created_at: Optional[datetime] = None

class VideoStatus(BaseModel):
    """Video processing status"""
    id: str
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None