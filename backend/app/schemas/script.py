"""Pydantic models for script generation"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class ScriptSlide(BaseModel):
    """Single slide in a script"""
    title: str
    subtitle: Optional[str] = None
    wrong_image_description: str
    right_image_description: str
    index: int


class ScriptGenerationRequest(BaseModel):
    """Request model for script generation"""
    topic: str = Field(..., min_length=10, description="Topic for content generation")
    num_slides: int = Field(default=5, ge=3, le=10, description="Number of slides")
    language: str = Field(default="vi", pattern="^(vi|en)$", description="Language code")

    @validator('topic')
    def validate_topic(cls, v):
        return v.strip()


class ScriptResponse(BaseModel):
    """Response model for script generation"""
    id: str
    topic: str
    slides: List[ScriptSlide]
    caption: Optional[str] = None
    created_at: datetime
    status: str = "completed"