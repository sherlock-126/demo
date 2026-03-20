"""
Main script generator class that orchestrates the content generation
"""

import time
from typing import Optional, Dict, Any

from .openai_client import OpenAIClient
from .prompt_builder import PromptBuilder
from .validator import Validator
from .storage import StorageHandler
from .models import ScriptModel, GenerationRequest, ErrorResponse
from .logger import (
    logger,
    log_generation_start,
    log_generation_success,
    log_generation_error
)


class ScriptGenerator:
    """Main orchestrator for script generation"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        storage_dir: Optional[str] = None
    ):
        """
        Initialize script generator

        Args:
            api_key: Optional OpenAI API key
            storage_dir: Optional directory for storing scripts
        """
        self.openai_client = OpenAIClient(api_key)
        self.prompt_builder = PromptBuilder()
        self.validator = Validator()
        self.storage = StorageHandler(storage_dir) if storage_dir else StorageHandler()

    def generate(
        self,
        topic: str,
        num_slides: int = 5,
        language: str = "vi",
        save_to_file: bool = True,
        temperature: float = 0.7
    ) -> ScriptModel:
        """
        Generate a content script

        Args:
            topic: The parenting topic
            num_slides: Number of slides to generate (1-10)
            language: Language code (vi or en)
            save_to_file: Whether to save the script to file
            temperature: GPT sampling temperature

        Returns:
            Generated ScriptModel

        Raises:
            ValueError: If validation fails
            Exception: If generation fails
        """
        start_time = time.time()

        try:
            # Validate inputs
            self.validator.validate_topic(topic)
            self.validator.validate_language(language)
            self.validator.validate_num_slides(num_slides)

            log_generation_start(topic, num_slides, language)

            # Build prompts
            prompts = self.prompt_builder.build_prompts(
                topic=topic,
                num_slides=num_slides,
                language=language
            )

            # Generate completion
            response = self.openai_client.generate_completion(
                system_prompt=prompts["system_prompt"],
                user_prompt=prompts["user_prompt"],
                temperature=temperature
            )

            # Validate response structure
            self.openai_client.validate_response(response)

            # Parse and validate output
            script = self.validator.validate_script_output(response["content"])

            # Update metadata
            script.metadata.tokens_used = response.get("tokens_used", 0)
            script.metadata.model = response.get("model", "gpt-4")
            script.metadata.language = language

            # Save to file if requested
            if save_to_file:
                file_path = self.storage.save_script(script)
                logger.info(f"Script saved to: {file_path}")

            duration = time.time() - start_time
            log_generation_success(topic, script.metadata.tokens_used, duration)

            return script

        except Exception as e:
            log_generation_error(topic, str(e))
            raise

    def generate_batch(
        self,
        topics: list[str],
        num_slides: int = 5,
        language: str = "vi",
        save_to_file: bool = True
    ) -> list[Dict[str, Any]]:
        """
        Generate scripts for multiple topics

        Args:
            topics: List of topics
            num_slides: Number of slides per script
            language: Language code
            save_to_file: Whether to save scripts

        Returns:
            List of results (success or error for each topic)
        """
        results = []

        for topic in topics:
            try:
                script = self.generate(
                    topic=topic,
                    num_slides=num_slides,
                    language=language,
                    save_to_file=save_to_file
                )
                results.append({
                    "topic": topic,
                    "status": "success",
                    "script": script
                })
            except Exception as e:
                results.append({
                    "topic": topic,
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"Failed to generate script for '{topic}': {e}")

            # Small delay between requests to avoid rate limiting
            time.sleep(1)

        return results

    def regenerate_with_feedback(
        self,
        script: ScriptModel,
        feedback: str,
        save_to_file: bool = True
    ) -> ScriptModel:
        """
        Regenerate a script with user feedback

        Args:
            script: Original script
            feedback: User feedback for improvement
            save_to_file: Whether to save the new script

        Returns:
            Regenerated ScriptModel
        """
        # Create enhanced prompt with feedback
        enhanced_topic = f"{script.topic}\n\nFeedback: {feedback}"

        return self.generate(
            topic=enhanced_topic,
            num_slides=len(script.slides),
            language=script.metadata.language,
            save_to_file=save_to_file
        )

    def list_generated_scripts(
        self,
        limit: int = 10,
        topic_filter: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        List previously generated scripts

        Args:
            limit: Maximum number of scripts to return
            topic_filter: Optional topic filter

        Returns:
            List of script metadata
        """
        return self.storage.list_scripts(limit=limit, topic_filter=topic_filter)

    def load_script(self, filename: str) -> ScriptModel:
        """
        Load a previously generated script

        Args:
            filename: Script filename

        Returns:
            ScriptModel instance
        """
        return self.storage.load_script(filename)

    def export_script(
        self,
        script: ScriptModel,
        format: str = "json"
    ) -> str:
        """
        Export script in different formats

        Args:
            script: Script to export
            format: Export format (json, text)

        Returns:
            Formatted string
        """
        return self.storage.export_script(script, format)

    def validate_request(self, request: GenerationRequest) -> bool:
        """
        Validate a generation request

        Args:
            request: GenerationRequest model

        Returns:
            True if valid

        Raises:
            ValueError: If invalid
        """
        return self.validator.validate_generation_request(request)