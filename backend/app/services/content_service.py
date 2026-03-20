"""Service wrapper for content_generator module"""

import sys
import os
import json
import uuid
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, "/app")

from content_generator.generator import ScriptGenerator
from content_generator.models import Script
from app.core.config import settings
from app.core.tasks import Task


class ContentService:
    """Service for content generation"""

    def __init__(self):
        self.api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")

    async def generate_script(
        self,
        task: Task,
        topic: str,
        num_slides: int = 5,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """Generate script from topic"""
        try:
            # Update task progress
            task.update_progress(10)

            # Initialize generator
            generator = ScriptGenerator(api_key=self.api_key)

            # Generate script
            task.update_progress(30)
            script = generator.generate(
                topic=topic,
                num_slides=num_slides,
                language=language
            )

            task.update_progress(80)

            # Save to file
            script_id = str(uuid.uuid4())
            output_path = os.path.join(settings.data_dir, f"{script_id}.json")

            # Ensure directory exists
            os.makedirs(settings.data_dir, exist_ok=True)

            # Convert to dict and save
            script_data = {
                "id": script_id,
                "topic": topic,
                "slides": [
                    {
                        "title": slide.title,
                        "subtitle": slide.subtitle,
                        "wrong_image_description": slide.wrong_image_description,
                        "right_image_description": slide.right_image_description,
                        "index": i
                    }
                    for i, slide in enumerate(script.slides)
                ],
                "caption": script.caption,
                "created_at": datetime.utcnow().isoformat()
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)

            task.update_progress(100)

            return script_data

        except Exception as e:
            raise Exception(f"Script generation failed: {str(e)}")


# Global service instance
content_service = ContentService()