"""
Pytest fixtures for testing
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock

from content_generator.models import ScriptModel, Slide, SideContent, ScriptMetadata


@pytest.fixture
def sample_topic():
    """Sample topic for testing"""
    return "Cách dạy con không la mắng"


@pytest.fixture
def sample_script_data():
    """Sample script data for testing"""
    return {
        "topic": "Cách dạy con không la mắng",
        "main_title": "Test Title",
        "subtitle": "Test Subtitle",
        "slides": [
            {
                "left_side": {
                    "description": "Test wrong description that is long enough",
                    "text": "Wrong behavior",
                    "label": "SAI"
                },
                "right_side": {
                    "description": "Test right description that is long enough",
                    "text": "Right behavior",
                    "label": "ĐÚNG"
                }
            }
        ],
        "metadata": {
            "generated_at": datetime.now(),
            "model": "gpt-4",
            "tokens_used": 100,
            "language": "vi",
            "prompt_version": "1.0"
        }
    }


@pytest.fixture
def sample_script_model(sample_script_data):
    """Sample ScriptModel instance"""
    return ScriptModel(**sample_script_data)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "content": {
            "topic": "Test Topic",
            "main_title": "Test Title",
            "subtitle": "Test Subtitle",
            "slides": [
                {
                    "left_side": {
                        "description": "Wrong approach description",
                        "text": "Wrong text",
                        "label": "SAI"
                    },
                    "right_side": {
                        "description": "Right approach description",
                        "text": "Right text",
                        "label": "ĐÚNG"
                    }
                }
            ]
        },
        "raw_content": '{"topic": "Test Topic"}',
        "tokens_used": 150,
        "model": "gpt-4-turbo-preview",
        "duration": 2.5
    }


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock OpenAI client"""
    client = Mock()
    client.generate_completion = Mock(return_value=mock_openai_response)
    client.validate_response = Mock(return_value=True)
    return client


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporary data directory for testing"""
    data_dir = tmp_path / "data"
    scripts_dir = data_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    return data_dir


@pytest.fixture
def mock_config(temp_data_dir):
    """Mock configuration"""
    config = Mock()
    config.openai_api_key = "sk-test-key"
    config.openai_model = "gpt-4"
    config.max_retries = 3
    config.timeout_seconds = 30
    config.log_level = "INFO"
    config.data_dir = temp_data_dir
    config.scripts_dir = temp_data_dir / "scripts"
    config.logs_dir = temp_data_dir / "logs"
    config.templates_dir = Path("templates")
    config.cache_enabled = False
    config.is_production = False
    return config


@pytest.fixture
def sample_prompts():
    """Sample prompts for testing"""
    return {
        "system_prompt": "You are a content creator...",
        "user_prompt": "Create content about: Test Topic"
    }