"""
Prompt builder for OpenAI API calls
"""

from pathlib import Path
from typing import Dict, Any
from .config import config


class PromptBuilder:
    """Build prompts for OpenAI API"""

    def __init__(self, templates_dir: Path = None):
        """Initialize prompt builder"""
        self.templates_dir = templates_dir or config.templates_dir
        self._load_templates()

    def _load_templates(self):
        """Load prompt templates from files"""
        system_prompt_file = self.templates_dir / "system_prompt.txt"
        user_prompt_file = self.templates_dir / "user_prompt.txt"

        if system_prompt_file.exists():
            with open(system_prompt_file, "r", encoding="utf-8") as f:
                self.system_template = f.read()
        else:
            self.system_template = self._get_default_system_prompt()

        if user_prompt_file.exists():
            with open(user_prompt_file, "r", encoding="utf-8") as f:
                self.user_template = f.read()
        else:
            self.user_template = self._get_default_user_prompt()

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt if template not found"""
        return """You are an expert content creator specializing in educational parenting content for TikTok. Your task is to transform parenting topics into engaging "Right vs Wrong" comparison scripts that educate parents.

You create content in the style of popular parenting education accounts that use split-screen comparisons to show incorrect vs correct parenting approaches. Each comparison should be:
- Clear and educational
- Based on modern parenting best practices
- Culturally appropriate for Vietnamese audiences
- Visually descriptive for image generation
- Concise but impactful

Your output must be a valid JSON object with exactly the specified structure. Focus on creating practical, actionable advice that parents can immediately apply."""

    def _get_default_user_prompt(self) -> str:
        """Get default user prompt if template not found"""
        return """Create a TikTok content script about: "{topic}"

Language: {language}
Number of slides: {num_slides}

Generate a JSON response with this EXACT structure:
{{
    "topic": "{topic}",
    "main_title": "A bold, attention-grabbing title in {language_name}",
    "subtitle": "A supporting headline that adds context in {language_name}",
    "slides": [
        {{
            "left_side": {{
                "description": "Detailed description for image generation showing the WRONG approach",
                "text": "Short overlay text describing the wrong behavior",
                "label": "{wrong_label}"
            }},
            "right_side": {{
                "description": "Detailed description for image generation showing the RIGHT approach",
                "text": "Short overlay text describing the correct behavior",
                "label": "{right_label}"
            }}
        }}
    ]
}}

Create exactly {num_slides} slides. Respond ONLY with the JSON object."""

    def build_prompts(
        self,
        topic: str,
        num_slides: int = 5,
        language: str = "vi"
    ) -> Dict[str, str]:
        """
        Build system and user prompts

        Args:
            topic: The parenting topic
            num_slides: Number of slides to generate
            language: Language code (vi or en)

        Returns:
            Dictionary with system_prompt and user_prompt
        """
        # Language-specific configurations
        language_config = {
            "vi": {
                "language_name": "Vietnamese",
                "wrong_label": "SAI",
                "right_label": "ĐÚNG"
            },
            "en": {
                "language_name": "English",
                "wrong_label": "WRONG",
                "right_label": "RIGHT"
            }
        }

        lang_cfg = language_config.get(language, language_config["vi"])

        # Format user prompt with variables
        user_prompt = self.user_template.format(
            topic=topic,
            num_slides=num_slides,
            language=language,
            language_name=lang_cfg["language_name"],
            wrong_label=lang_cfg["wrong_label"],
            right_label=lang_cfg["right_label"]
        )

        return {
            "system_prompt": self.system_template,
            "user_prompt": user_prompt
        }

    def build_refinement_prompt(self, original_response: str, issue: str) -> str:
        """
        Build a prompt to refine a problematic response

        Args:
            original_response: The original response that had issues
            issue: Description of the issue

        Returns:
            Refinement prompt
        """
        return f"""The previous response had the following issue: {issue}

Please correct the response and ensure it:
1. Is valid JSON
2. Contains all required fields
3. Has the exact structure specified
4. Uses the correct language and labels

Original response for reference:
{original_response}

Provide ONLY the corrected JSON response, no additional text."""