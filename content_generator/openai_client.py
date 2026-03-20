"""
OpenAI API client with retry logic and error handling
"""

import json
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from .config import config
from .logger import logger, log_api_retry
from .models import ErrorResponse


class OpenAIClient:
    """OpenAI API client with retry logic"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client"""
        self.api_key = api_key or config.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = config.openai_model
        self.timeout = config.timeout_seconds
        self.max_retries = config.max_retries

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
            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                # Extract JSON from the response if wrapped in markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                json_content = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.debug(f"Raw response: {content}")
                raise ValueError(f"Invalid JSON response from OpenAI: {e}")

            return {
                "content": json_content,
                "raw_content": content,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "model": response.model,
                "duration": duration
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate the response structure

        Args:
            response: Response dictionary from OpenAI

        Returns:
            True if valid, raises ValueError if not
        """
        content = response.get("content", {})

        required_fields = ["topic", "main_title", "subtitle", "slides"]
        for field in required_fields:
            if field not in content:
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(content["slides"], list):
            raise ValueError("Slides must be a list")

        if len(content["slides"]) == 0:
            raise ValueError("At least one slide is required")

        for i, slide in enumerate(content["slides"]):
            if "left_side" not in slide or "right_side" not in slide:
                raise ValueError(f"Slide {i} missing left_side or right_side")

            for side in ["left_side", "right_side"]:
                side_content = slide[side]
                required_side_fields = ["description", "text", "label"]
                for field in required_side_fields:
                    if field not in side_content:
                        raise ValueError(
                            f"Slide {i} {side} missing field: {field}"
                        )

        return True

    def create_error_response(self, error: str, suggestion: str) -> ErrorResponse:
        """Create a standardized error response"""
        return ErrorResponse(
            error="openai_api_error",
            message=str(error),
            details={"client": "openai", "model": self.model},
            suggestion=suggestion
        )