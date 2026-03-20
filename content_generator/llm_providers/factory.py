"""
Factory for creating LLM providers
"""

import os
from typing import Optional, Dict, Any

from ..config import config as app_config
from ..logger import logger
from .base import LLMProvider
from .models import ProviderType
from .openai_provider import OpenAIProvider
from .cli_provider import CLIProvider
from .mock_provider import MockProvider
from .exceptions import ProviderNotAvailable


def get_llm_provider(
    provider_type: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> LLMProvider:
    """
    Get an LLM provider instance based on configuration

    Args:
        provider_type: Override provider type (defaults to env var)
        config: Provider-specific configuration

    Returns:
        LLMProvider instance

    Raises:
        ProviderNotAvailable: If provider cannot be created
    """
    # Determine provider type
    if provider_type is None:
        provider_type = os.getenv("LLM_PROVIDER", "openai_api")

    logger.info(f"Creating LLM provider: {provider_type}")

    try:
        provider_type_enum = ProviderType(provider_type)
    except ValueError:
        available = ", ".join([p.value for p in ProviderType])
        raise ProviderNotAvailable(
            message=f"Invalid provider type: {provider_type}",
            provider="factory",
            details={"available_providers": available}
        )

    # Create provider based on type
    try:
        if provider_type_enum == ProviderType.OPENAI_API:
            return _create_openai_provider(config)

        elif provider_type_enum == ProviderType.CLI_CHATGPT:
            return _create_cli_chatgpt_provider(config)

        elif provider_type_enum == ProviderType.REVCHATGPT:
            return _create_revchatgpt_provider(config)

        elif provider_type_enum == ProviderType.MOCK:
            return MockProvider(config)

        else:
            raise ProviderNotAvailable(
                message=f"Provider not implemented: {provider_type}",
                provider="factory"
            )

    except Exception as e:
        if isinstance(e, ProviderNotAvailable):
            raise
        raise ProviderNotAvailable(
            message=f"Failed to create provider: {e}",
            provider="factory",
            details={"provider_type": provider_type, "error": str(e)}
        )


def _create_openai_provider(config: Optional[Dict[str, Any]] = None) -> OpenAIProvider:
    """Create OpenAI API provider"""
    api_key = os.getenv("OPENAI_API_KEY") or (config.get("api_key") if config else None)

    if not api_key:
        raise ProviderNotAvailable(
            message="OpenAI API key not found",
            provider="openai_api",
            details={"env_var": "OPENAI_API_KEY"}
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    # Merge config
    provider_config = {
        "timeout": int(os.getenv("TIMEOUT_SECONDS", "30")),
        "max_retries": int(os.getenv("MAX_RETRIES", "3"))
    }
    if config:
        provider_config.update(config)

    return OpenAIProvider(
        api_key=api_key,
        model=model,
        config=provider_config
    )


def _create_cli_chatgpt_provider(config: Optional[Dict[str, Any]] = None) -> CLIProvider:
    """Create CLI-based ChatGPT provider"""
    cli_command = os.getenv("CHATGPT_CLI_COMMAND", "chatgpt-cli")

    # Merge config
    provider_config = {
        "timeout": int(os.getenv("CLI_TIMEOUT", "60"))
    }
    if config:
        provider_config.update(config)

    class ChatGPTCLIProvider(CLIProvider):
        """ChatGPT CLI specific implementation"""

        def __init__(self, cli_command: str, config: Optional[Dict[str, Any]] = None):
            super().__init__(cli_command, config)
            self.provider_name = "cli_chatgpt"

        def _build_command(self, system_prompt: str, user_prompt: str, **kwargs) -> list:
            """Build chatgpt-cli specific command"""
            # Combine prompts for chatgpt-cli
            combined = f"{system_prompt}\n\n{user_prompt}\n\nPlease respond with a JSON object."
            return [self.cli_command, "ask", combined]

    return ChatGPTCLIProvider(cli_command, provider_config)


def _create_revchatgpt_provider(config: Optional[Dict[str, Any]] = None) -> CLIProvider:
    """Create revChatGPT provider (placeholder for now)"""
    # This would require additional implementation for browser automation
    # For now, return a CLI provider that could call a revChatGPT script

    cli_command = os.getenv("REVCHATGPT_COMMAND", "python -m revchatgpt")

    provider_config = {
        "timeout": int(os.getenv("REVCHATGPT_TIMEOUT", "90"))
    }
    if config:
        provider_config.update(config)

    class RevChatGPTProvider(CLIProvider):
        """RevChatGPT specific implementation"""

        def __init__(self, cli_command: str, config: Optional[Dict[str, Any]] = None):
            super().__init__(cli_command, config)
            self.provider_name = "revchatgpt"

    return RevChatGPTProvider(cli_command, provider_config)