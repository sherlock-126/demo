"""
Tests for the validator module
"""

import pytest
from content_generator.validator import Validator
from content_generator.models import GenerationRequest


class TestValidator:
    """Test input/output validation"""

    def test_validate_topic_valid(self):
        """Test valid topic validation"""
        assert Validator.validate_topic("Cách dạy con")
        assert Validator.validate_topic("How to teach children patience")
        assert Validator.validate_topic("A" * 200)  # Max length

    def test_validate_topic_invalid(self):
        """Test invalid topic validation"""
        with pytest.raises(ValueError, match="non-empty string"):
            Validator.validate_topic("")

        with pytest.raises(ValueError, match="at least 3 characters"):
            Validator.validate_topic("AB")

        with pytest.raises(ValueError, match="exceed 200 characters"):
            Validator.validate_topic("A" * 201)

    def test_validate_language(self):
        """Test language validation"""
        assert Validator.validate_language("vi")
        assert Validator.validate_language("en")

        with pytest.raises(ValueError, match="Language must be"):
            Validator.validate_language("fr")

    def test_validate_num_slides(self):
        """Test slide number validation"""
        assert Validator.validate_num_slides(1)
        assert Validator.validate_num_slides(5)
        assert Validator.validate_num_slides(10)

        with pytest.raises(ValueError, match="At least 1 slide"):
            Validator.validate_num_slides(0)

        with pytest.raises(ValueError, match="Maximum 10 slides"):
            Validator.validate_num_slides(11)

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        assert Validator.sanitize_filename("Hello World") == "hello_world"
        assert Validator.sanitize_filename("Test@#$123") == "test123"
        assert Validator.sanitize_filename("A very long " * 10)[:50]

    def test_validate_api_key(self):
        """Test API key validation"""
        assert Validator.validate_api_key("sk-" + "x" * 40)

        with pytest.raises(ValueError, match="API key is required"):
            Validator.validate_api_key("")

        with pytest.raises(ValueError, match="Invalid API key format"):
            Validator.validate_api_key("not-an-api-key")

        with pytest.raises(ValueError, match="too short"):
            Validator.validate_api_key("sk-123")

    def test_validate_generation_request(self):
        """Test complete request validation"""
        request = GenerationRequest(
            topic="Valid topic",
            num_slides=5,
            language="vi"
        )
        assert Validator.validate_generation_request(request)

        # Invalid request
        with pytest.raises(ValueError):
            invalid_request = GenerationRequest(
                topic="No",  # Too short
                num_slides=5,
                language="vi"
            )
            Validator.validate_generation_request(invalid_request)