"""
Tests for the OpenAI client module
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from content_generator.openai_client import OpenAIClient


class TestOpenAIClient:
    """Test OpenAIClient class"""

    @patch('content_generator.openai_client.config')
    def test_init_with_api_key(self, mock_config):
        """Test client initialization with API key"""
        mock_config.openai_api_key = "default-key"
        client = OpenAIClient(api_key="test-key")
        assert client.api_key == "test-key"

    @patch('content_generator.openai_client.config')
    def test_init_without_api_key(self, mock_config):
        """Test client initialization without API key fails"""
        mock_config.openai_api_key = None
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIClient()

    @patch('content_generator.openai_client.OpenAI')
    @patch('content_generator.openai_client.config')
    def test_generate_completion_success(self, mock_config, mock_openai_class):
        """Test successful completion generation"""
        # Setup config
        mock_config.openai_api_key = "test-key"
        mock_config.openai_model = "gpt-4"
        mock_config.timeout_seconds = 30
        mock_config.max_retries = 3

        # Setup OpenAI mock
        mock_openai_instance = Mock()
        mock_openai_class.return_value = mock_openai_instance

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"topic": "Test", "main_title": "Title"}'))]
        mock_response.usage = Mock(total_tokens=100)
        mock_response.model = "gpt-4"
        mock_openai_instance.chat.completions.create.return_value = mock_response

        # Execute
        client = OpenAIClient()
        result = client.generate_completion("System prompt", "User prompt")

        # Verify
        assert result["content"]["topic"] == "Test"
        assert result["tokens_used"] == 100
        assert "duration" in result

    @patch('content_generator.openai_client.OpenAI')
    @patch('content_generator.openai_client.config')
    def test_generate_completion_json_parsing(self, mock_config, mock_openai_class):
        """Test JSON parsing from markdown code blocks"""
        mock_config.openai_api_key = "test-key"
        mock_config.openai_model = "gpt-4"
        mock_config.timeout_seconds = 30

        mock_openai_instance = Mock()
        mock_openai_class.return_value = mock_openai_instance

        # Test with ```json wrapper
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(
            content='```json\n{"topic": "Test"}\n```'
        ))]
        mock_response.usage = Mock(total_tokens=50)
        mock_response.model = "gpt-4"
        mock_openai_instance.chat.completions.create.return_value = mock_response

        client = OpenAIClient()
        result = client.generate_completion("System", "User")

        assert result["content"]["topic"] == "Test"

    def test_validate_response_valid(self):
        """Test valid response validation"""
        client = OpenAIClient(api_key="test-key")
        response = {
            "content": {
                "topic": "Test",
                "main_title": "Title",
                "subtitle": "Subtitle",
                "slides": [{
                    "left_side": {
                        "description": "Desc",
                        "text": "Text",
                        "label": "SAI"
                    },
                    "right_side": {
                        "description": "Desc",
                        "text": "Text",
                        "label": "ĐÚNG"
                    }
                }]
            }
        }
        assert client.validate_response(response) is True

    def test_validate_response_missing_field(self):
        """Test validation with missing required field"""
        client = OpenAIClient(api_key="test-key")
        response = {
            "content": {
                "topic": "Test",
                "main_title": "Title"
                # Missing subtitle and slides
            }
        }
        with pytest.raises(ValueError, match="Missing required field"):
            client.validate_response(response)

    def test_validate_response_empty_slides(self):
        """Test validation with empty slides"""
        client = OpenAIClient(api_key="test-key")
        response = {
            "content": {
                "topic": "Test",
                "main_title": "Title",
                "subtitle": "Subtitle",
                "slides": []
            }
        }
        with pytest.raises(ValueError, match="At least one slide"):
            client.validate_response(response)

    def test_validate_response_invalid_slide_structure(self):
        """Test validation with invalid slide structure"""
        client = OpenAIClient(api_key="test-key")
        response = {
            "content": {
                "topic": "Test",
                "main_title": "Title",
                "subtitle": "Subtitle",
                "slides": [{
                    "left_side": {
                        "description": "Desc",
                        "text": "Text"
                        # Missing label
                    },
                    "right_side": {
                        "description": "Desc",
                        "text": "Text",
                        "label": "ĐÚNG"
                    }
                }]
            }
        }
        with pytest.raises(ValueError, match="missing field"):
            client.validate_response(response)