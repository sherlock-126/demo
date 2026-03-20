"""
Python API interface for the content generator
"""

from typing import Optional, List, Dict, Any
from .generator import ScriptGenerator as _ScriptGenerator
from .models import ScriptModel, GenerationRequest, ErrorResponse


class ScriptGenerator:
    """
    Public API for script generation

    Example usage:
        from content_generator import ScriptGenerator

        generator = ScriptGenerator(api_key="sk-...")
        script = generator.generate(
            topic="Cách dạy con không la mắng",
            num_slides=5,
            language="vi"
        )
        print(script.main_title)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the script generator

        Args:
            api_key: OpenAI API key (optional, can use env variable)
        """
        self._generator = _ScriptGenerator(api_key=api_key)

    def generate(
        self,
        topic: str,
        num_slides: int = 5,
        language: str = "vi",
        save_to_file: bool = True
    ) -> ScriptModel:
        """
        Generate a content script for TikTok

        Args:
            topic: The parenting topic to create content about
            num_slides: Number of comparison slides (1-10)
            language: Language code ('vi' for Vietnamese, 'en' for English)
            save_to_file: Whether to save the script to disk

        Returns:
            ScriptModel containing the generated content

        Raises:
            ValueError: If inputs are invalid
            Exception: If generation fails
        """
        return self._generator.generate(
            topic=topic,
            num_slides=num_slides,
            language=language,
            save_to_file=save_to_file
        )

    def generate_batch(
        self,
        topics: List[str],
        num_slides: int = 5,
        language: str = "vi"
    ) -> List[Dict[str, Any]]:
        """
        Generate scripts for multiple topics

        Args:
            topics: List of parenting topics
            num_slides: Number of slides per script
            language: Language code

        Returns:
            List of results with status and script/error for each topic
        """
        return self._generator.generate_batch(
            topics=topics,
            num_slides=num_slides,
            language=language
        )

    def list_scripts(
        self,
        limit: int = 10,
        topic_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List previously generated scripts

        Args:
            limit: Maximum number of scripts to return
            topic_filter: Optional filter by topic substring

        Returns:
            List of script metadata
        """
        return self._generator.list_generated_scripts(
            limit=limit,
            topic_filter=topic_filter
        )

    def load_script(self, filename: str) -> ScriptModel:
        """
        Load a previously generated script from disk

        Args:
            filename: Name of the script file

        Returns:
            ScriptModel instance
        """
        return self._generator.load_script(filename)

    def export_script(
        self,
        script: ScriptModel,
        format: str = "json"
    ) -> str:
        """
        Export a script in different formats

        Args:
            script: ScriptModel to export
            format: Export format ('json' or 'text')

        Returns:
            Formatted string representation
        """
        return self._generator.export_script(script, format)

    def regenerate_with_feedback(
        self,
        script: ScriptModel,
        feedback: str
    ) -> ScriptModel:
        """
        Regenerate a script with user feedback

        Args:
            script: Original script
            feedback: User feedback for improvement

        Returns:
            New ScriptModel with improvements
        """
        return self._generator.regenerate_with_feedback(script, feedback)

    @staticmethod
    def from_request(request: GenerationRequest) -> ScriptModel:
        """
        Generate a script from a GenerationRequest model

        Args:
            request: GenerationRequest with all parameters

        Returns:
            Generated ScriptModel
        """
        generator = ScriptGenerator()
        return generator.generate(
            topic=request.topic,
            num_slides=request.num_slides,
            language=request.language,
            save_to_file=not request.force_regenerate
        )