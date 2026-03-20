"""
Tests for video assembly module
"""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch, MagicMock

from video_assembly import VideoConfig, VideoError, VideoAssembler, VideoAPI
from video_assembly.models import TimingConfig, AudioConfig, EncodingConfig


class TestVideoConfig:
    """Test VideoConfig model"""

    def test_default_config(self):
        """Test default configuration values"""
        config = VideoConfig()
        assert config.width == 1080
        assert config.height == 1920
        assert config.fps == 60
        assert config.timing.duration_per_slide == 3.0
        assert config.transitions.type == 'fade'

    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        config = VideoConfig(width=720, height=1280, fps=30)
        assert config.width == 720

        # Invalid values should raise error
        with pytest.raises(Exception):
            VideoConfig(width=-100)

    def test_config_from_dict(self):
        """Test creating config from dictionary"""
        data = {
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'timing': {'duration_per_slide': 5.0}
        }
        config = VideoConfig(**data)
        assert config.fps == 30
        assert config.timing.duration_per_slide == 5.0


class TestVideoError:
    """Test VideoError exception"""

    def test_error_creation(self):
        """Test creating VideoError"""
        error = VideoError(
            error_type='test_error',
            message='Test error message',
            details={'key': 'value'},
            suggestion='Try this',
            recoverable=True
        )
        assert error.error_type == 'test_error'
        assert error.message == 'Test error message'
        assert error.recoverable is True
        assert str(error) == 'Test error message'


class TestImageProcessor:
    """Test image processing"""

    def test_scan_directory_no_images(self):
        """Test scanning directory with no images"""
        from video_assembly.processors import ImageProcessor

        processor = ImageProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Empty directory should raise error
            with pytest.raises(VideoError) as exc_info:
                processor.scan_directory(tmpdir)
            assert exc_info.value.error_type == 'no_images_found'

    def test_scan_directory_with_images(self):
        """Test scanning directory with valid images"""
        from video_assembly.processors import ImageProcessor
        from PIL import Image

        processor = ImageProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test images
            for i in range(3):
                img = Image.new('RGB', (100, 100), color='red')
                img.save(Path(tmpdir) / f'test_{i}.png')

            # Should find 3 images
            images = processor.scan_directory(tmpdir)
            assert len(images) == 3
            assert all('test_' in img for img in images)


class TestAudioProcessor:
    """Test audio processing"""

    def test_scan_audio_directory(self):
        """Test scanning for audio files"""
        from video_assembly.processors import AudioProcessor

        processor = AudioProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fake audio files
            (Path(tmpdir) / 'music1.mp3').touch()
            (Path(tmpdir) / 'music2.wav').touch()
            (Path(tmpdir) / 'not_audio.txt').touch()

            files = processor.scan_audio_directory(tmpdir)
            assert len(files) == 2
            assert any('music1.mp3' in f for f in files)
            assert any('music2.wav' in f for f in files)


class TestTransitionEngine:
    """Test transition calculations"""

    def test_calculate_duration(self):
        """Test total duration calculation"""
        from video_assembly.processors import TransitionEngine
        from video_assembly.models import TransitionConfig

        config = TransitionConfig(type='fade')
        engine = TransitionEngine(config)

        # Single slide
        duration = engine.calculate_total_duration(1, 3.0, 0.5)
        assert duration == 3.0

        # Multiple slides with transitions
        duration = engine.calculate_total_duration(3, 3.0, 0.5)
        assert duration == 8.0  # 3*3 - 2*0.5

        # No transitions
        config.type = 'none'
        engine = TransitionEngine(config)
        duration = engine.calculate_total_duration(3, 3.0, 0.5)
        assert duration == 9.0  # 3*3


class TestFFmpegValidator:
    """Test FFmpeg validation"""

    @patch('subprocess.run')
    def test_validate_ffmpeg_not_found(self, mock_run):
        """Test when FFmpeg is not installed"""
        from video_assembly.ffmpeg import FFmpegValidator

        mock_run.side_effect = FileNotFoundError()
        validator = FFmpegValidator()

        with pytest.raises(VideoError) as exc_info:
            validator.validate()
        assert exc_info.value.error_type == 'ffmpeg_not_found'

    @patch('subprocess.run')
    def test_validate_ffmpeg_success(self, mock_run):
        """Test successful FFmpeg validation"""
        from video_assembly.ffmpeg import FFmpegValidator

        # Mock successful ffmpeg checks
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'ffmpeg version 4.4.0\nlibx264\naac\nscale\nfade'
        mock_run.return_value = mock_result

        validator = FFmpegValidator()
        assert validator.validate() is True


class TestVideoAPI:
    """Test public API"""

    def test_api_initialization(self):
        """Test API initialization with different config types"""
        # Default config
        api = VideoAPI()
        assert api.config.width == 1080

        # With VideoConfig object
        config = VideoConfig(fps=30)
        api = VideoAPI(config)
        assert api.config.fps == 30

        # With dictionary
        api = VideoAPI({'fps': 24})
        assert api.config.fps == 24

    @patch('video_assembly.assembler.VideoAssembler.create_video')
    def test_generate_video(self, mock_create):
        """Test video generation through API"""
        from video_assembly.models import VideoResult

        # Mock successful video creation
        mock_result = VideoResult(
            output_path=Path('/tmp/video.mp4'),
            duration=10.0,
            frame_count=600,
            file_size=1000000,
            images_used=['img1.png', 'img2.png'],
            music_used='music.mp3',
            encoding_time=5.0,
            metadata={}
        )
        mock_create.return_value = mock_result

        api = VideoAPI()
        result = api.generate_video('images/', 'output.mp4')

        assert result.output_path == Path('/tmp/video.mp4')
        assert result.duration == 10.0
        mock_create.assert_called_once()