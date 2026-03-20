"""
Mock provider for testing
"""

import time
import json
from typing import Dict, Any, Optional

from .base import LLMProvider


class MockProvider(LLMProvider):
    """Mock provider for testing purposes"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize mock provider"""
        super().__init__(config)
        self.provider_name = "mock"
        self.response_delay = config.get("response_delay", 0.1) if config else 0.1

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Generate a mock completion

        Args:
            system_prompt: System instructions
            user_prompt: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dict containing mock response
        """
        start_time = time.time()

        # Simulate processing delay
        time.sleep(self.response_delay)

        # Generate mock response based on prompts
        mock_content = {
            "topic": "Mock parenting topic from user prompt",
            "main_title": "SAI vs ĐÚNG: Cách Dạy Con Mock",
            "subtitle": "Phương pháp giáo dục con hiệu quả (Mock)",
            "slides": [
                {
                    "left_side": {
                        "description": "Mock wrong approach image",
                        "text": "La mắng, quát tháo (Mock)",
                        "label": "SAI"
                    },
                    "right_side": {
                        "description": "Mock correct approach image",
                        "text": "Giải thích nhẹ nhàng (Mock)",
                        "label": "ĐÚNG"
                    }
                },
                {
                    "left_side": {
                        "description": "Mock wrong behavior image",
                        "text": "Bỏ mặc con (Mock)",
                        "label": "SAI"
                    },
                    "right_side": {
                        "description": "Mock correct behavior image",
                        "text": "Đồng hành cùng con (Mock)",
                        "label": "ĐÚNG"
                    }
                }
            ]
        }

        raw_content = json.dumps(mock_content, ensure_ascii=False, indent=2)
        duration = time.time() - start_time

        return {
            "content": mock_content,
            "raw_content": raw_content,
            "tokens_used": 500,  # Mock token count
            "model": "mock-gpt",
            "duration": duration,
            "provider": self.provider_name
        }