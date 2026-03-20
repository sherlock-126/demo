"""
OpenAI API provider implementation
"""

import time
from typing import Dict, Any, Optional
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from ..logger import logger, log_api_retry
from .base import LLMProvider
from .exceptions import AuthenticationError, ProviderTimeoutError


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", config: Optional[Dict[str, Any]] = None):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key
            model: Model to use
            config: Additional configuration
        """
        super().__init__(config)

        if not api_key:
            raise AuthenticationError(
                message="OpenAI API key is required",
                provider="openai_api",
                details={"error": "missing_api_key"}
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.timeout = config.get("timeout", 30) if config else 30
        self.max_retries = config.get("max_retries", 3) if config else 3
        self.provider_name = "openai_api"

    def _log_retry(self, retry_state):
        """Log retry attempts"""
        attempt = retry_state.attempt_number
        exception = retry_state.outcome.exception()
        log_api_retry(attempt, self.max_retries, str(exception))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Generate a completion from OpenAI

        Args:
            system_prompt: System instructions
            user_prompt: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dict containing the response and metadata
        """
        try:
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
                response_format={"type": "text"}
            )

            duration = time.time() - start_time
            raw_content = response.choices[0].message.content

            # Parse the response
            content = self.parse_response(raw_content)

            return {
                "content": content,
                "raw_content": raw_content,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "model": response.model,
                "duration": duration,
                "provider": self.provider_name
            }

        except Exception as e:
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                raise AuthenticationError(
                    message=f"OpenAI authentication failed: {e}",
                    provider=self.provider_name,
                    details={"error": str(e)}
                )
            elif "timeout" in str(e).lower():
                raise ProviderTimeoutError(
                    message=f"OpenAI request timed out: {e}",
                    provider=self.provider_name,
                    details={"timeout": self.timeout}
                )
            else:
                logger.error(f"OpenAI API error: {e}")
                raise