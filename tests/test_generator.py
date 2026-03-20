"""
Tests for the generator module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from content_generator.generator import ScriptGenerator
from content_generator.models import ScriptModel


class TestScriptGenerator:
    """Test ScriptGenerator class"""

    @patch('content_generator.generator.OpenAIClient')
    @patch('content_generator.generator.PromptBuilder')
    @patch('content_generator.generator.StorageHandler')
    def test_init(self, mock_storage, mock_prompt_builder, mock_openai):
        """Test generator initialization"""
        generator = ScriptGenerator(api_key="test-key")

        mock_openai.assert_called_once_with("test-key")
        mock_prompt_builder.assert_called_once()
        mock_storage.assert_called_once()

    @patch('content_generator.generator.OpenAIClient')
    @patch('content_generator.generator.PromptBuilder')
    @patch('content_generator.generator.StorageHandler')
    def test_generate_success(self, mock_storage, mock_prompt_builder, mock_openai):
        """Test successful script generation"""
        # Setup mocks
        mock_openai_instance = Mock()
        mock_openai.return_value = mock_openai_instance
        mock_openai_instance.generate_completion.return_value = {
            "content": {
                "topic": "Test Topic",
                "main_title": "Test Title",
                "subtitle": "Test Subtitle",
                "slides": [{
                    "left_side": {
                        "description": "Wrong approach with detailed description",
                        "text": "Wrong text",
                        "label": "SAI"
                    },
                    "right_side": {
                        "description": "Right approach with detailed description",
                        "text": "Right text",
                        "label": "ĐÚNG"
                    }
                }]
            },
            "tokens_used": 100,
            "model": "gpt-4"
        }
        mock_openai_instance.validate_response.return_value = True

        mock_prompt_instance = Mock()
        mock_prompt_builder.return_value = mock_prompt_instance
        mock_prompt_instance.build_prompts.return_value = {
            "system_prompt": "System",
            "user_prompt": "User"
        }

        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance

        # Execute
        generator = ScriptGenerator()
        script = generator.generate("Test Topic", num_slides=1)

        # Verify
        assert isinstance(script, ScriptModel)
        assert script.topic == "Test Topic"
        assert script.main_title == "Test Title"
        assert len(script.slides) == 1

    @patch('content_generator.generator.OpenAIClient')
    def test_generate_validation_error(self, mock_openai):
        """Test generation with validation error"""
        generator = ScriptGenerator()

        with pytest.raises(ValueError, match="at least 3 characters"):
            generator.generate("AB")  # Too short topic

    @patch('content_generator.generator.OpenAIClient')
    @patch('content_generator.generator.PromptBuilder')
    @patch('content_generator.generator.StorageHandler')
    def test_generate_batch(self, mock_storage, mock_prompt_builder, mock_openai):
        """Test batch generation"""
        # Setup mocks similar to test_generate_success
        mock_openai_instance = Mock()
        mock_openai.return_value = mock_openai_instance
        mock_openai_instance.generate_completion.return_value = {
            "content": {
                "topic": "Topic",
                "main_title": "Title",
                "subtitle": "Subtitle",
                "slides": [{
                    "left_side": {
                        "description": "Long enough description for testing",
                        "text": "Text",
                        "label": "SAI"
                    },
                    "right_side": {
                        "description": "Long enough description for testing",
                        "text": "Text",
                        "label": "ĐÚNG"
                    }
                }]
            },
            "tokens_used": 100,
            "model": "gpt-4"
        }
        mock_openai_instance.validate_response.return_value = True

        mock_prompt_instance = Mock()
        mock_prompt_builder.return_value = mock_prompt_instance
        mock_prompt_instance.build_prompts.return_value = {
            "system_prompt": "System",
            "user_prompt": "User"
        }

        # Execute
        generator = ScriptGenerator()
        results = generator.generate_batch(["Topic 1", "Topic 2"])

        # Verify
        assert len(results) == 2
        assert all("status" in r for r in results)
        assert all("topic" in r for r in results)