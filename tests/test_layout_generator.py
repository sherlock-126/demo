"""
Tests for layout generator
"""

import pytest
from pathlib import Path
import json
from PIL import Image
from layout_generator import LayoutGenerator, LayoutConfig
from layout_generator.models import RenderResult
from content_generator.models import ScriptModel, Slide, SideContent


@pytest.fixture
def sample_script():
    """Create a sample script for testing"""
    return ScriptModel(
        topic="Test Topic",
        main_title="TEST TITLE",
        subtitle="Test subtitle",
        slides=[
            Slide(
                left_side=SideContent(
                    description="Test wrong description",
                    text="Wrong content",
                    label="SAI"
                ),
                right_side=SideContent(
                    description="Test right description",
                    text="Right content",
                    label="ĐÚNG"
                )
            )
        ]
    )


@pytest.fixture
def test_config():
    """Create a test configuration"""
    return {
        "layout": {
            "width": 1080,
            "height": 1920,
            "padding": 60,
            "split_ratio": 0.5
        },
        "colors": {
            "background": {
                "main": "#FFFFFF",
                "wrong": "#FFE8E8",
                "right": "#E8FFE8"
            },
            "text": {
                "title": "#000000",
                "subtitle": "#666666",
                "label_wrong": "#FF0000",
                "label_right": "#00FF00",
                "content": "#333333"
            }
        },
        "fonts": {
            "title": {"path": "assets/fonts/Roboto-Bold.ttf", "size": 72},
            "subtitle": {"path": "assets/fonts/Roboto-Regular.ttf", "size": 48},
            "label": {"path": "assets/fonts/Roboto-Black.ttf", "size": 60},
            "text": {"path": "assets/fonts/Roboto-Medium.ttf", "size": 42}
        },
        "icons": {
            "wrong": "assets/icons/x-mark.png",
            "right": "assets/icons/check-mark.png",
            "size": 100
        }
    }


class TestLayoutGenerator:
    """Test LayoutGenerator class"""

    def test_initialization_with_config(self, test_config):
        """Test initializing with config dictionary"""
        generator = LayoutGenerator(config=test_config)
        assert generator is not None

    def test_initialization_without_config(self):
        """Test initializing with default config"""
        generator = LayoutGenerator()
        assert generator is not None

    def test_generate_single_slide(self, sample_script, test_config, tmp_path):
        """Test generating a single slide"""
        generator = LayoutGenerator(config=test_config)

        # Generate slide
        img = generator.generate_single_slide(
            sample_script.slides[0].dict(),
            slide_number=1,
            total_slides=1,
            title=sample_script.main_title,
            subtitle=sample_script.subtitle
        )

        assert isinstance(img, Image.Image)
        assert img.size == (1080, 1920)

    def test_generate_all_slides(self, sample_script, test_config, tmp_path):
        """Test generating all slides from script"""
        generator = LayoutGenerator(config=test_config)
        output_dir = tmp_path / "output"

        # Generate all slides
        result = generator.generate_from_script(
            sample_script,
            output_dir=str(output_dir)
        )

        assert isinstance(result, RenderResult)
        assert len(result.images) == 1
        assert all(Path(img).exists() for img in result.images)

    def test_preview_slide(self, sample_script, test_config):
        """Test preview functionality"""
        generator = LayoutGenerator(config=test_config)

        # Preview first slide
        img = generator.preview_slide(sample_script, slide_index=0)

        assert isinstance(img, Image.Image)
        assert img.size == (1080, 1920)

    def test_generate_from_json_file(self, tmp_path, sample_script, test_config):
        """Test generating from JSON file"""
        # Save script to file
        script_file = tmp_path / "test_script.json"
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(sample_script.to_json(), f)

        generator = LayoutGenerator(config=test_config)
        output_dir = tmp_path / "output"

        # Generate from file
        result = generator.generate_from_script(
            str(script_file),
            output_dir=str(output_dir)
        )

        assert isinstance(result, RenderResult)
        assert len(result.images) == 1

    def test_vietnamese_text_rendering(self, test_config, tmp_path):
        """Test rendering Vietnamese text with tone marks"""
        script = ScriptModel(
            topic="Kiểm tra tiếng Việt",
            main_title="TIẾNG VIỆT CÓ DẤU",
            subtitle="Ả ã ạ ă ằ ẳ ẵ ặ â ầ ẩ ẫ ậ",
            slides=[
                Slide(
                    left_side=SideContent(
                        description="Test",
                        text="Sai cách làm",
                        label="SAI"
                    ),
                    right_side=SideContent(
                        description="Test",
                        text="Đúng cách làm",
                        label="ĐÚNG"
                    )
                )
            ]
        )

        generator = LayoutGenerator(config=test_config)
        output_dir = tmp_path / "output"

        # Should not raise error
        result = generator.generate_from_script(
            script,
            output_dir=str(output_dir)
        )

        assert len(result.images) == 1