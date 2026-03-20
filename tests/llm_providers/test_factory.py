"""
Tests for LLM provider factory
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from content_generator.llm_providers import get_llm_provider
from content_generator.llm_providers.exceptions import ProviderNotAvailable
from content_generator.llm_providers.openai_provider import OpenAIProvider
from content_generator.llm_providers.mock_provider import MockProvider


class TestProviderFactory:
    """Test provider factory functionality"""

    def test_get_mock_provider(self):
        """Test creating mock provider"""
        provider = get_llm_provider("mock")
        assert isinstance(provider, MockProvider)
        assert provider.provider_name == "mock"

    @patch.dict(os.environ, {"LLM_PROVIDER": "mock"})
    def test_get_provider_from_env(self):
        """Test getting provider from environment variable"""
        provider = get_llm_provider()
        assert isinstance(provider, MockProvider)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_get_openai_provider(self):
        """Test creating OpenAI provider"""
        with patch("content_generator.llm_providers.openai_provider.OpenAI"):
            provider = get_llm_provider("openai_api")
            assert isinstance(provider, OpenAIProvider)
            assert provider.provider_name == "openai_api"

    def test_invalid_provider_type(self):
        """Test invalid provider type raises error"""
        with pytest.raises(ProviderNotAvailable) as exc:
            get_llm_provider("invalid_provider")
        assert "Invalid provider type" in str(exc.value)

    def test_openai_without_key(self):
        """Test OpenAI provider without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ProviderNotAvailable) as exc:
                get_llm_provider("openai_api")
            assert "API key not found" in str(exc.value)