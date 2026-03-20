"""
Abstract base class for LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import json
import re

from ..logger import logger
from .models import LLMResponse
from .exceptions import ResponseParseError


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize provider with configuration

        Args:
            config: Provider-specific configuration
        """
        self.config = config or {}
        self.provider_name = self.__class__.__name__

    @abstractmethod
    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Generate a completion from the LLM

        Args:
            system_prompt: System instructions
            user_prompt: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dict containing response and metadata
        """
        pass

    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate the response structure

        Args:
            response: Response dictionary from provider

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

    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse raw response into structured format

        Args:
            raw_response: Raw text response from provider

        Returns:
            Parsed JSON content

        Raises:
            ResponseParseError: If parsing fails
        """
        try:
            # Try to extract JSON from various formats
            content = raw_response

            # Extract from markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # Try to find JSON object in text
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, content)
            if matches:
                # Try the longest match first (likely the complete JSON)
                for match in sorted(matches, key=len, reverse=True):
                    try:
                        return json.loads(match)
                    except json.JSONDecodeError:
                        continue

            # Direct parse attempt
            return json.loads(content)

        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            logger.debug(f"Raw response: {raw_response[:500]}...")
            raise ResponseParseError(
                message=f"Failed to parse JSON response: {e}",
                provider=self.provider_name,
                details={"raw_response_preview": raw_response[:500]}
            )

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def create_response(
        self,
        content: Dict[str, Any],
        raw_content: str,
        duration: float,
        model: str = "unknown",
        tokens_used: Optional[int] = None
    ) -> LLMResponse:
        """
        Create standardized response object

        Args:
            content: Parsed content
            raw_content: Raw response text
            duration: Processing time
            model: Model identifier
            tokens_used: Token count (optional)

        Returns:
            LLMResponse object
        """
        if tokens_used is None:
            tokens_used = self.estimate_tokens(raw_content)

        return LLMResponse(
            content=content,
            raw_content=raw_content,
            tokens_used=tokens_used,
            model=model,
            duration=duration,
            provider=self.provider_name
        )