"""
Image processing and validation
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image
from ..models import VideoError


class ImageProcessor:
    """Process and validate images for video generation"""

    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.webp'}

    def __init__(self, target_resolution: Tuple[int, int] = (1080, 1920)):
        """
        Initialize image processor

        Args:
            target_resolution: Target resolution (width, height)
        """
        self.target_resolution = target_resolution

    def scan_directory(self, directory: str) -> List[str]:
        """
        Scan directory for valid image files

        Args:
            directory: Directory path to scan

        Returns:
            Sorted list of image file paths

        Raises:
            VideoError: If no valid images found
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise VideoError(
                error_type='directory_not_found',
                message=f'Directory not found: {directory}',
                suggestion='Check the directory path',
                recoverable=False
            )

        # Find all image files
        image_files = []
        for ext in self.SUPPORTED_FORMATS:
            image_files.extend(dir_path.glob(f'*{ext}'))
            image_files.extend(dir_path.glob(f'*{ext.upper()}'))

        if not image_files:
            raise VideoError(
                error_type='no_images_found',
                message=f'No images found in directory: {directory}',
                details={'supported_formats': list(self.SUPPORTED_FORMATS)},
                suggestion='Add PNG or JPG images to the directory',
                recoverable=False
            )

        # Sort by name (numerical if possible)
        def sort_key(path):
            name = path.stem
            # Try to extract number from filename
            import re
            numbers = re.findall(r'\d+', name)
            if numbers:
                return int(numbers[0])
            return name

        image_files.sort(key=sort_key)

        # Validate and return paths
        valid_files = []
        for img_path in image_files:
            if self._validate_image(img_path):
                valid_files.append(str(img_path))

        if not valid_files:
            raise VideoError(
                error_type='no_valid_images',
                message='No valid images found after validation',
                suggestion='Check that images are not corrupted',
                recoverable=False
            )

        return valid_files

    def _validate_image(self, image_path: Path) -> bool:
        """
        Validate image file

        Args:
            image_path: Path to image file

        Returns:
            True if valid, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                # Check if image can be loaded
                img.verify()
                return True
        except Exception:
            return False

    def preprocess_image(
        self,
        image_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Preprocess image for video generation

        Args:
            image_path: Input image path
            output_path: Optional output path for processed image

        Returns:
            Path to processed image
        """
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background

                # Resize if significantly different from target
                if abs(img.width - self.target_resolution[0]) > 100 or \
                   abs(img.height - self.target_resolution[1]) > 100:
                    img = self._resize_and_pad(img)

                # Save processed image if output path provided
                if output_path:
                    img.save(output_path, 'JPEG', quality=95)
                    return output_path

                return image_path

        except Exception as e:
            raise VideoError(
                error_type='image_processing_failed',
                message=f'Failed to process image: {image_path}',
                details={'error': str(e)},
                recoverable=True
            )

    def _resize_and_pad(self, img: Image.Image) -> Image.Image:
        """
        Resize and pad image to target resolution

        Args:
            img: PIL Image object

        Returns:
            Resized and padded image
        """
        target_w, target_h = self.target_resolution

        # Calculate scaling to fit
        scale = min(target_w / img.width, target_h / img.height)
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)

        # Resize image
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Create padded image
        padded = Image.new('RGB', (target_w, target_h), (0, 0, 0))
        x = (target_w - new_w) // 2
        y = (target_h - new_h) // 2
        padded.paste(img, (x, y))

        return padded

    def create_thumbnail(
        self,
        image_path: str,
        output_path: str,
        size: Tuple[int, int] = (320, 568)
    ):
        """
        Create thumbnail from image

        Args:
            image_path: Source image path
            output_path: Output thumbnail path
            size: Thumbnail size (width, height)
        """
        try:
            with Image.open(image_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(output_path, 'JPEG', quality=85)
        except Exception as e:
            raise VideoError(
                error_type='thumbnail_creation_failed',
                message=f'Failed to create thumbnail: {str(e)}',
                recoverable=True
            )