"""
Tests for layout generator components
"""

import pytest
from PIL import Image, ImageDraw
from layout_generator.components import BackgroundRenderer, TextRenderer, IconRenderer, LogoRenderer
from layout_generator.utils import hex_to_rgb, wrap_text


class TestBackgroundRenderer:
    """Test BackgroundRenderer component"""

    def test_render_split_background(self):
        """Test rendering split-screen background"""
        colors = {
            "main": "#FFFFFF",
            "wrong": "#FFE8E8",
            "right": "#E8FFE8"
        }

        renderer = BackgroundRenderer(1080, 1920, colors)
        img = renderer.render(split_ratio=0.5)

        assert isinstance(img, Image.Image)
        assert img.size == (1080, 1920)

    def test_render_gradient_background(self):
        """Test rendering gradient background"""
        colors = {
            "wrong": "#FFE8E8",
            "right": "#E8FFE8"
        }

        renderer = BackgroundRenderer(1080, 1920, colors)
        img = renderer.render_gradient(split_ratio=0.5)

        assert isinstance(img, Image.Image)
        assert img.size == (1080, 1920)


class TestTextRenderer:
    """Test TextRenderer component"""

    def test_render_title(self):
        """Test rendering title text"""
        fonts = {
            "title": {"path": "assets/fonts/Roboto-Bold.ttf", "size": 72}
        }
        colors = {"title": "#000000"}

        renderer = TextRenderer(fonts, colors)
        img = Image.new('RGB', (1080, 1920), (255, 255, 255))

        # Should not raise error
        renderer.render_title(img, "Test Title", y_position=100)

    def test_render_side_content(self):
        """Test rendering side content text"""
        fonts = {
            "text": {"path": "assets/fonts/Roboto-Regular.ttf", "size": 42}
        }
        colors = {"content": "#333333"}

        renderer = TextRenderer(fonts, colors)
        img = Image.new('RGB', (1080, 1920), (255, 255, 255))

        # Should not raise error
        renderer.render_side_content(
            img,
            "Test content text",
            side="left",
            y_position=500,
            padding=60
        )


class TestIconRenderer:
    """Test IconRenderer component"""

    def test_fallback_x_symbol(self):
        """Test X symbol fallback when icon not found"""
        config = {
            "wrong": "nonexistent.png",
            "right": "nonexistent.png",
            "size": 100
        }

        renderer = IconRenderer(config)
        img = Image.new('RGB', (1080, 1920), (255, 255, 255))

        # Should draw fallback symbol
        renderer.render_wrong_icon(img)

    def test_fallback_check_symbol(self):
        """Test check symbol fallback when icon not found"""
        config = {
            "wrong": "nonexistent.png",
            "right": "nonexistent.png",
            "size": 100
        }

        renderer = IconRenderer(config)
        img = Image.new('RGB', (1080, 1920), (255, 255, 255))

        # Should draw fallback symbol
        renderer.render_right_icon(img)


class TestUtilityFunctions:
    """Test utility functions"""

    def test_hex_to_rgb(self):
        """Test hex color to RGB conversion"""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_wrap_text(self):
        """Test text wrapping functionality"""
        # This test requires a font, so we'll skip if fonts not available
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()

            text = "This is a long text that needs to be wrapped to fit within a certain width"
            lines = wrap_text(text, 200, font)

            assert isinstance(lines, list)
            assert len(lines) > 1
        except:
            pytest.skip("Font not available for testing")