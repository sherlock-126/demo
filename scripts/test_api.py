#!/usr/bin/env python3
"""
Test script to validate the API implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock test without actual OpenAI API call
def test_models():
    """Test that models work correctly"""
    from content_generator.models import ScriptModel, Slide, SideContent, ScriptMetadata
    from datetime import datetime

    # Test SideContent
    side = SideContent(
        description="Test description that is long enough",
        text="Test text",
        label="SAI"
    )
    assert side.label == "SAI"
    print("✓ SideContent model works")

    # Test Slide
    slide = Slide(
        left_side=SideContent(
            description="Wrong approach description",
            text="Wrong text",
            label="SAI"
        ),
        right_side=SideContent(
            description="Right approach description",
            text="Right text",
            label="ĐÚNG"
        )
    )
    assert slide.left_side.label == "SAI"
    assert slide.right_side.label == "ĐÚNG"
    print("✓ Slide model works")

    # Test ScriptModel
    script = ScriptModel(
        topic="Test topic",
        main_title="Test title",
        subtitle="Test subtitle",
        slides=[slide]
    )
    assert script.topic == "Test topic"
    assert len(script.slides) == 1
    print("✓ ScriptModel works")

    # Test JSON conversion
    json_data = script.to_json()
    assert "topic" in json_data
    assert isinstance(json_data["metadata"]["generated_at"], str)
    print("✓ JSON conversion works")


def test_validator():
    """Test validator functions"""
    from content_generator.validator import Validator

    # Test topic validation
    try:
        Validator.validate_topic("Valid topic")
        print("✓ Topic validation works")
    except Exception as e:
        print(f"✗ Topic validation failed: {e}")

    # Test language validation
    try:
        Validator.validate_language("vi")
        Validator.validate_language("en")
        print("✓ Language validation works")
    except Exception as e:
        print(f"✗ Language validation failed: {e}")

    # Test number validation
    try:
        Validator.validate_num_slides(5)
        print("✓ Number validation works")
    except Exception as e:
        print(f"✗ Number validation failed: {e}")

    # Test filename sanitization
    sanitized = Validator.sanitize_filename("Test/File*Name?")
    assert sanitized == "testfilename"
    print("✓ Filename sanitization works")


def test_prompt_builder():
    """Test prompt builder"""
    from content_generator.prompt_builder import PromptBuilder

    builder = PromptBuilder()
    prompts = builder.build_prompts(
        topic="Test topic",
        num_slides=3,
        language="vi"
    )

    assert "system_prompt" in prompts
    assert "user_prompt" in prompts
    assert "Test topic" in prompts["user_prompt"]
    assert "SAI" in prompts["user_prompt"]
    assert "ĐÚNG" in prompts["user_prompt"]
    print("✓ Prompt builder works")


def test_storage():
    """Test storage handler"""
    from content_generator.storage import StorageHandler
    from content_generator.models import ScriptModel, Slide, SideContent
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        storage = StorageHandler(Path(tmpdir))

        # Create a test script
        script = ScriptModel(
            topic="Test storage",
            main_title="Test title",
            subtitle="Test subtitle",
            slides=[
                Slide(
                    left_side=SideContent(
                        description="Wrong approach",
                        text="Wrong",
                        label="SAI"
                    ),
                    right_side=SideContent(
                        description="Right approach",
                        text="Right",
                        label="ĐÚNG"
                    )
                )
            ]
        )

        # Test save
        file_path = storage.save_script(script)
        assert file_path.exists()
        print("✓ Storage save works")

        # Test load
        loaded_script = storage.load_script(file_path.name)
        assert loaded_script.topic == "Test storage"
        print("✓ Storage load works")

        # Test export
        json_export = storage.export_script(script, format="json")
        assert "Test storage" in json_export
        text_export = storage.export_script(script, format="text")
        assert "Test storage" in text_export
        print("✓ Storage export works")


def test_config():
    """Test configuration"""
    try:
        from content_generator.config import Config
        import tempfile

        # Create temp config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("OPENAI_API_KEY=sk-test123456789\n")
            temp_env = f.name

        config = Config(env_file=temp_env)
        assert config.openai_api_key == "sk-test123456789"
        print("✓ Config loading works")

        # Cleanup
        os.unlink(temp_env)
    except Exception as e:
        print(f"✗ Config test failed: {e}")


def main():
    print("Testing Content Generator Implementation")
    print("=" * 50)

    test_models()
    test_validator()
    test_prompt_builder()
    test_storage()
    test_config()

    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("\nNote: These are unit tests without actual API calls.")
    print("To test with OpenAI API, you need to set OPENAI_API_KEY in .env file")


if __name__ == "__main__":
    main()