"""
Data models for the content generator
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class SideContent(BaseModel):
    """Content for one side of the split-screen comparison"""
    description: str = Field(..., description="Detailed prompt for image generation")
    text: str = Field(..., description="Overlay text to display on the image")
    label: str = Field(..., description="Label for the side (SAI or ĐÚNG)")

    @validator('label')
    def validate_label(cls, v):
        if v not in ['SAI', 'ĐÚNG', 'WRONG', 'RIGHT']:
            raise ValueError('Label must be SAI, ĐÚNG, WRONG, or RIGHT')
        return v


class Slide(BaseModel):
    """A single comparison slide with left and right sides"""
    left_side: SideContent
    right_side: SideContent

    @validator('left_side')
    def validate_left_label(cls, v):
        if v.label not in ['SAI', 'WRONG']:
            v.label = 'SAI'
        return v

    @validator('right_side')
    def validate_right_label(cls, v):
        if v.label not in ['ĐÚNG', 'RIGHT']:
            v.label = 'ĐÚNG'
        return v


class ScriptMetadata(BaseModel):
    """Metadata about the script generation"""
    generated_at: datetime = Field(default_factory=datetime.now)
    model: str = Field(default="gpt-4-turbo-preview")
    tokens_used: int = Field(default=0)
    language: str = Field(default="vi")
    prompt_version: str = Field(default="1.0")


class ScriptModel(BaseModel):
    """Complete script model for TikTok content"""
    topic: str = Field(..., description="The input parenting topic")
    main_title: str = Field(..., description="Bold, attention-grabbing title")
    subtitle: str = Field(..., description="Supporting headline")
    slides: List[Slide] = Field(..., description="List of comparison slides")
    metadata: ScriptMetadata = Field(default_factory=ScriptMetadata)

    @validator('slides')
    def validate_slides(cls, v):
        if not v:
            raise ValueError('At least one slide is required')
        if len(v) > 10:
            raise ValueError('Maximum 10 slides allowed')
        return v

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        data = self.dict()
        data['metadata']['generated_at'] = data['metadata']['generated_at'].isoformat()
        return data


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="User-friendly error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Technical details")
    suggestion: str = Field(..., description="Suggestion for fixing the error")
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        data = self.dict()
        data['timestamp'] = data['timestamp'].isoformat()
        return data


class GenerationRequest(BaseModel):
    """Request model for script generation"""
    topic: str = Field(..., min_length=3, max_length=200)
    num_slides: int = Field(default=5, ge=1, le=10)
    language: str = Field(default="vi", pattern="^(vi|en)$")
    force_regenerate: bool = Field(default=False)