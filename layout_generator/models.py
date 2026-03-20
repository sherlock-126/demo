"""
Data models for layout generator
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Tuple, Optional, List, Any


class FontConfig(BaseModel):
    """Font configuration"""
    path: str = Field(..., description="Path to font file")
    size: int = Field(..., description="Font size in pixels")
    fallback: Optional[str] = Field(None, description="Fallback font path")


class ColorConfig(BaseModel):
    """Color configuration"""
    background: Dict[str, str] = Field(..., description="Background colors")
    text: Dict[str, str] = Field(..., description="Text colors")


class IconConfig(BaseModel):
    """Icon configuration"""
    wrong: str = Field(..., description="Path to wrong/X icon")
    right: str = Field(..., description="Path to right/check icon")
    size: int = Field(default=100, description="Icon size in pixels")


class LogoConfig(BaseModel):
    """Logo configuration"""
    path: str = Field(..., description="Path to logo image")
    position: str = Field(default="top-center", description="Logo position")
    size: Tuple[int, int] = Field(..., description="Logo size (width, height)")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)

    @validator('position')
    def validate_position(cls, v):
        valid = ["top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right"]
        if v not in valid:
            raise ValueError(f"Position must be one of {valid}")
        return v


class LayoutDimensions(BaseModel):
    """Layout dimensions configuration"""
    width: int = Field(default=1080)
    height: int = Field(default=1920)
    padding: int = Field(default=60)
    split_ratio: float = Field(default=0.5, ge=0.0, le=1.0)


class LayoutConfig(BaseModel):
    """Complete layout configuration"""
    layout: LayoutDimensions = Field(default_factory=LayoutDimensions)
    colors: ColorConfig
    fonts: Dict[str, FontConfig]
    icons: IconConfig
    logo: Optional[LogoConfig] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary"""
        return cls(**data)


class RenderResult(BaseModel):
    """Result of rendering operation"""
    images: List[str] = Field(..., description="Paths to saved images")
    thumbnails: List[str] = Field(default_factory=list, description="Paths to thumbnails")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RenderError(Exception):
    """Custom exception for rendering errors"""
    def __init__(self, error_type: str, message: str, details: dict = None, recovery_action: str = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.recovery_action = recovery_action
        super().__init__(self.message)