"""
Input and output validation for the content generator
"""

import re
from typing import Any, Dict, List
from .models import ScriptModel, GenerationRequest, ErrorResponse


class Validator:
    """Validate inputs and outputs"""

    @staticmethod
    def validate_topic(topic: str) -> bool:
        """
        Validate topic input

        Args:
            topic: The input topic

        Returns:
            True if valid

        Raises:
            ValueError: If invalid
        """
        if not topic or not isinstance(topic, str):
            raise ValueError("Topic must be a non-empty string")

        topic = topic.strip()

        if len(topic) < 3:
            raise ValueError("Topic must be at least 3 characters long")

        if len(topic) > 200:
            raise ValueError("Topic must not exceed 200 characters")

        # Check for inappropriate content keywords (basic filter)
        inappropriate_keywords = [
            "violence", "abuse", "inappropriate", "sexual",
            "bạo lực", "lạm dụng", "không phù hợp"
        ]

        topic_lower = topic.lower()
        for keyword in inappropriate_keywords:
            if keyword in topic_lower:
                raise ValueError(
                    f"Topic contains inappropriate content: {keyword}"
                )

        return True

    @staticmethod
    def validate_language(language: str) -> bool:
        """
        Validate language code

        Args:
            language: Language code

        Returns:
            True if valid

        Raises:
            ValueError: If invalid
        """
        valid_languages = ["vi", "en"]
        if language not in valid_languages:
            raise ValueError(
                f"Language must be one of: {', '.join(valid_languages)}"
            )
        return True

    @staticmethod
    def validate_num_slides(num_slides: int) -> bool:
        """
        Validate number of slides

        Args:
            num_slides: Number of slides

        Returns:
            True if valid

        Raises:
            ValueError: If invalid
        """
        if not isinstance(num_slides, int):
            raise ValueError("Number of slides must be an integer")

        if num_slides < 1:
            raise ValueError("At least 1 slide is required")

        if num_slides > 10:
            raise ValueError("Maximum 10 slides allowed")

        return True

    @staticmethod
    def validate_generation_request(request: GenerationRequest) -> bool:
        """
        Validate a complete generation request

        Args:
            request: Generation request model

        Returns:
            True if valid

        Raises:
            ValueError: If invalid
        """
        Validator.validate_topic(request.topic)
        Validator.validate_language(request.language)
        Validator.validate_num_slides(request.num_slides)
        return True

    @staticmethod
    def validate_script_output(data: Dict[str, Any]) -> ScriptModel:
        """
        Validate and parse script output

        Args:
            data: Raw script data

        Returns:
            Validated ScriptModel

        Raises:
            ValueError: If invalid
        """
        try:
            # Create ScriptModel which will validate structure
            script = ScriptModel(**data)

            # Additional validation
            if len(script.slides) == 0:
                raise ValueError("Script must contain at least one slide")

            # Validate descriptions are detailed enough
            for i, slide in enumerate(script.slides):
                if len(slide.left_side.description) < 20:
                    raise ValueError(
                        f"Slide {i+1} left description too short "
                        f"(min 20 chars)"
                    )
                if len(slide.right_side.description) < 20:
                    raise ValueError(
                        f"Slide {i+1} right description too short "
                        f"(min 20 chars)"
                    )

                # Validate text overlay length
                if len(slide.left_side.text.split()) > 15:
                    raise ValueError(
                        f"Slide {i+1} left text too long (max 15 words)"
                    )
                if len(slide.right_side.text.split()) > 15:
                    raise ValueError(
                        f"Slide {i+1} right text too long (max 15 words)"
                    )

            return script

        except Exception as e:
            raise ValueError(f"Invalid script output: {e}")

    @staticmethod
    def sanitize_filename(text: str) -> str:
        """
        Sanitize text for use as filename

        Args:
            text: Input text

        Returns:
            Sanitized filename
        """
        # Remove special characters
        text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores
        text = re.sub(r'[-\s]+', '_', text)
        # Truncate to reasonable length
        text = text[:50]
        return text.lower()

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate OpenAI API key format

        Args:
            api_key: API key

        Returns:
            True if valid format

        Raises:
            ValueError: If invalid
        """
        if not api_key:
            raise ValueError("API key is required")

        if not api_key.startswith("sk-"):
            raise ValueError("Invalid API key format (should start with 'sk-')")

        if len(api_key) < 20:
            raise ValueError("API key appears to be too short")

        return True