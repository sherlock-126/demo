"""Service wrapper for layout_generator module"""

import sys
import os
import json
from typing import List, Dict, Any
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, "/app")

from layout_generator.generator import LayoutGenerator
from layout_generator.models import SlideContent
from app.core.config import settings
from app.core.tasks import Task


class LayoutService:
    """Service for image layout generation"""

    def __init__(self):
        self.generator = LayoutGenerator()

    async def generate_images(
        self,
        task: Task,
        script_id: str
    ) -> List[str]:
        """Generate images from script"""
        try:
            # Load script
            script_path = os.path.join(settings.data_dir, f"{script_id}.json")
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script {script_id} not found")

            with open(script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)

            # Ensure output directory exists
            os.makedirs(settings.output_dir, exist_ok=True)

            # Generate images for each slide
            images = []
            total_slides = len(script_data['slides'])

            for i, slide_data in enumerate(script_data['slides']):
                # Update progress
                progress = int((i / total_slides) * 100)
                task.update_progress(progress)

                # Create slide content
                slide = SlideContent(
                    title=slide_data['title'],
                    subtitle=slide_data.get('subtitle', ''),
                    wrong_image_description=slide_data['wrong_image_description'],
                    right_image_description=slide_data['right_image_description']
                )

                # Generate image
                output_path = os.path.join(
                    settings.output_dir,
                    f"{script_id}_slide_{i+1:02d}.png"
                )

                self.generator.generate_slide(slide, output_path)
                images.append(output_path)

            task.update_progress(100)
            return images

        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")


# Global service instance
layout_service = LayoutService()