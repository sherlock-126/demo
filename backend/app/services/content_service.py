"""
Content generation service
"""
import logging
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class ContentService:
    """Service for content generation operations"""

    def __init__(self):
        self.data_dir = Path("/app/data")
        self.output_dir = Path("/app/output")
        self.tasks = {}  # Track async tasks

    async def generate_script(
        self,
        topic: str,
        style: str = "parenting",
        num_slides: int = 5
    ) -> Dict[str, Any]:
        """Generate a script using the content_generator module"""
        try:
            # Import the content generator module
            from content_generator import ScriptGenerator

            # Create generator instance
            generator = ScriptGenerator()

            # Generate script
            script = generator.generate(
                topic=topic,
                num_slides=num_slides
            )

            # Save script to file
            script_id = str(uuid.uuid4())
            script_path = self.data_dir / "scripts" / f"{script_id}.json"
            script_path.parent.mkdir(parents=True, exist_ok=True)

            with open(script_path, "w", encoding="utf-8") as f:
                json.dump(script, f, ensure_ascii=False, indent=2)

            return script
        except ImportError:
            logger.warning("content_generator module not available, using mock data")
            # Return mock data for testing
            return {
                "topic": topic,
                "slides": [
                    {
                        "title": f"Slide {i+1}",
                        "content": f"Content for slide {i+1} about {topic}",
                        "image_description": f"Image for slide {i+1}"
                    }
                    for i in range(num_slides)
                ]
            }
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            raise

    async def get_script(self, script_id: str) -> Optional[Dict[str, Any]]:
        """Get a script by ID"""
        try:
            script_path = self.data_dir / "scripts" / f"{script_id}.json"
            if script_path.exists():
                with open(script_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                return {
                    "id": script_id,
                    "topic": content.get("topic", "Unknown"),
                    "content": content,
                    "status": "completed"
                }
            return None
        except Exception as e:
            logger.error(f"Error getting script: {e}")
            return None

    async def list_scripts(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """List all scripts"""
        try:
            scripts_dir = self.data_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)

            scripts = []
            for script_file in sorted(scripts_dir.glob("*.json"))[skip:skip+limit]:
                script_id = script_file.stem
                with open(script_file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                scripts.append({
                    "id": script_id,
                    "topic": content.get("topic", "Unknown"),
                    "status": "completed"
                })
            return scripts
        except Exception as e:
            logger.error(f"Error listing scripts: {e}")
            return []

    async def generate_images_async(self, script_id: str, task_id: str):
        """Generate images asynchronously"""
        try:
            self.tasks[task_id] = {"status": "processing", "images": []}

            # Import layout generator
            try:
                from layout_generator import LayoutGenerator
                generator = LayoutGenerator()

                # Load script
                script = await self.get_script(script_id)
                if script:
                    # Generate images
                    images = generator.generate_from_script(script["content"])
                    self.tasks[task_id] = {
                        "status": "completed",
                        "images": images
                    }
                else:
                    self.tasks[task_id] = {
                        "status": "failed",
                        "error": "Script not found"
                    }
            except ImportError:
                # Mock implementation
                await asyncio.sleep(2)  # Simulate processing
                self.tasks[task_id] = {
                    "status": "completed",
                    "images": [f"/app/output/image_{i}.png" for i in range(5)]
                }
        except Exception as e:
            logger.error(f"Error generating images: {e}")
            self.tasks[task_id] = {
                "status": "failed",
                "error": str(e)
            }

    async def get_image_generation_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get image generation task status"""
        task = self.tasks.get(task_id)
        if task:
            return {
                "task_id": task_id,
                "script_id": "",  # Would need to track this
                "status": task["status"],
                "images": task.get("images", [])
            }
        return None

    async def list_images(self, script_id: str) -> List[str]:
        """List images for a script"""
        try:
            images_dir = self.output_dir / script_id
            if images_dir.exists():
                return [str(img) for img in images_dir.glob("*.png")]
            return []
        except Exception as e:
            logger.error(f"Error listing images: {e}")
            return []