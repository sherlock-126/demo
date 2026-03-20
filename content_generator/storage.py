"""
File system operations for storing generated scripts
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from slugify import slugify

from .config import config
from .models import ScriptModel
from .logger import logger


class StorageHandler:
    """Handle file system operations for scripts"""

    def __init__(self, scripts_dir: Path = None):
        """Initialize storage handler"""
        self.scripts_dir = scripts_dir or config.scripts_dir
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

    def save_script(
        self,
        script: ScriptModel,
        filename: Optional[str] = None
    ) -> Path:
        """
        Save a script to file

        Args:
            script: ScriptModel to save
            filename: Optional custom filename

        Returns:
            Path to saved file
        """
        if not filename:
            # Generate filename from timestamp and topic
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_slug = slugify(script.topic, max_length=50)
            filename = f"{timestamp}_{topic_slug}.json"

        file_path = self.scripts_dir / filename

        try:
            # Convert to JSON-serializable dict
            data = script.to_json()

            # Save to file with pretty printing
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Script saved to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to save script: {e}")
            # Try to save to stdout as fallback
            print(json.dumps(script.to_json(), ensure_ascii=False, indent=2))
            raise

    def load_script(self, filename: str) -> ScriptModel:
        """
        Load a script from file

        Args:
            filename: Filename to load

        Returns:
            ScriptModel instance
        """
        file_path = self.scripts_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Script file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert ISO timestamp back to datetime
        if "metadata" in data and "generated_at" in data["metadata"]:
            data["metadata"]["generated_at"] = datetime.fromisoformat(
                data["metadata"]["generated_at"]
            )

        return ScriptModel(**data)

    def list_scripts(
        self,
        limit: int = 10,
        topic_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List saved scripts

        Args:
            limit: Maximum number of scripts to return
            topic_filter: Optional topic substring to filter by

        Returns:
            List of script metadata
        """
        scripts = []

        # Get all JSON files
        script_files = sorted(
            self.scripts_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for script_file in script_files[:limit * 2]:  # Load more for filtering
            try:
                with open(script_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Apply topic filter if provided
                if topic_filter and topic_filter.lower() not in data.get("topic", "").lower():
                    continue

                scripts.append({
                    "filename": script_file.name,
                    "topic": data.get("topic", "Unknown"),
                    "main_title": data.get("main_title", ""),
                    "num_slides": len(data.get("slides", [])),
                    "generated_at": data.get("metadata", {}).get("generated_at"),
                    "file_path": str(script_file)
                })

                if len(scripts) >= limit:
                    break

            except Exception as e:
                logger.warning(f"Failed to read script {script_file}: {e}")
                continue

        return scripts

    def delete_script(self, filename: str) -> bool:
        """
        Delete a script file

        Args:
            filename: Filename to delete

        Returns:
            True if deleted successfully
        """
        file_path = self.scripts_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Script file not found: {file_path}")

        try:
            file_path.unlink()
            logger.info(f"Script deleted: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete script: {e}")
            raise

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics

        Returns:
            Dictionary with storage stats
        """
        script_files = list(self.scripts_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in script_files)

        return {
            "total_scripts": len(script_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "scripts_dir": str(self.scripts_dir)
        }

    def export_script(
        self,
        script: ScriptModel,
        format: str = "json"
    ) -> str:
        """
        Export script in different formats

        Args:
            script: ScriptModel to export
            format: Export format (json, text)

        Returns:
            Formatted string
        """
        if format == "json":
            return json.dumps(script.to_json(), ensure_ascii=False, indent=2)

        elif format == "text":
            # Human-readable text format
            lines = [
                f"Topic: {script.topic}",
                f"Title: {script.main_title}",
                f"Subtitle: {script.subtitle}",
                "",
                "Slides:",
                "-" * 50
            ]

            for i, slide in enumerate(script.slides, 1):
                lines.extend([
                    f"\nSlide {i}:",
                    f"  [{slide.left_side.label}] {slide.left_side.text}",
                    f"  Description: {slide.left_side.description[:100]}...",
                    "",
                    f"  [{slide.right_side.label}] {slide.right_side.text}",
                    f"  Description: {slide.right_side.description[:100]}...",
                    "-" * 50
                ])

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def cleanup_old_scripts(self, days: int = 30) -> int:
        """
        Clean up scripts older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of files deleted
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0

        for script_file in self.scripts_dir.glob("*.json"):
            if script_file.stat().st_mtime < cutoff_time:
                try:
                    script_file.unlink()
                    deleted_count += 1
                    logger.info(f"Cleaned up old script: {script_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete {script_file}: {e}")

        return deleted_count