"""
Tests for data models
"""

import pytest
from datetime import datetime
from content_generator.models import (
    SideContent, Slide, ScriptMetadata, ScriptModel, ErrorResponse, GenerationRequest
)


class TestModels:
    """Test Pydantic models"""

    def test_side_content(self):
        """Test SideContent model"""
        content = SideContent(
            description="A parent talking to child",
            text="Gentle conversation",
            label="ĐÚNG"
        )
        assert content.description == "A parent talking to child"
        assert content.text == "Gentle conversation"
        assert content.label == "ĐÚNG"

        # Invalid label
        with pytest.raises(ValueError):
            SideContent(
                description="test",
                text="test",
                label="INVALID"
            )

    def test_slide(self):
        """Test Slide model"""
        slide = Slide(
            left_side=SideContent(
                description="Wrong approach",
                text="Yelling",
                label="SAI"
            ),
            right_side=SideContent(
                description="Right approach",
                text="Calm talking",
                label="ĐÚNG"
            )
        )
        assert slide.left_side.label == "SAI"
        assert slide.right_side.label == "ĐÚNG"

    def test_script_model(self):
        """Test complete ScriptModel"""
        script = ScriptModel(
            topic="Test topic",
            main_title="Test Title",
            subtitle="Test Subtitle",
            slides=[
                Slide(
                    left_side=SideContent(
                        description="Wrong",
                        text="Wrong text",
                        label="SAI"
                    ),
                    right_side=SideContent(
                        description="Right",
                        text="Right text",
                        label="ĐÚNG"
                    )
                )
            ]
        )

        assert script.topic == "Test topic"
        assert len(script.slides) == 1
        assert script.metadata.language == "vi"

        # Test JSON conversion
        json_data = script.to_json()
        assert isinstance(json_data, dict)
        assert isinstance(json_data['metadata']['generated_at'], str)

    def test_script_model_validation(self):
        """Test ScriptModel validation"""
        # No slides - should fail
        with pytest.raises(ValueError, match="At least one slide"):
            ScriptModel(
                topic="Test",
                main_title="Title",
                subtitle="Subtitle",
                slides=[]
            )

        # Too many slides
        many_slides = [
            Slide(
                left_side=SideContent(description="L", text="L", label="SAI"),
                right_side=SideContent(description="R", text="R", label="ĐÚNG")
            )
            for _ in range(11)
        ]
        with pytest.raises(ValueError, match="Maximum 10 slides"):
            ScriptModel(
                topic="Test",
                main_title="Title",
                subtitle="Subtitle",
                slides=many_slides
            )

    def test_error_response(self):
        """Test ErrorResponse model"""
        error = ErrorResponse(
            error="api_error",
            message="API failed",
            details={"code": 500},
            suggestion="Check API key"
        )

        assert error.error == "api_error"
        assert error.details["code"] == 500

        # Test JSON conversion
        json_data = error.to_json()
        assert isinstance(json_data['timestamp'], str)

    def test_generation_request(self):
        """Test GenerationRequest model"""
        request = GenerationRequest(
            topic="Test topic",
            num_slides=5,
            language="vi"
        )

        assert request.topic == "Test topic"
        assert request.num_slides == 5
        assert request.language == "vi"
        assert request.force_regenerate is False

        # Test validation
        with pytest.raises(ValueError):
            GenerationRequest(
                topic="AB",  # Too short
                num_slides=5,
                language="vi"
            )

        with pytest.raises(ValueError):
            GenerationRequest(
                topic="Valid topic",
                num_slides=15,  # Too many
                language="vi"
            )