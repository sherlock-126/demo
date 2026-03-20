"""
Base class for CLI-based LLM providers
"""

import subprocess
import json
import time
import shlex
from typing import Dict, Any, Optional
import os

from ..logger import logger
from .base import LLMProvider
from .models import CLIExecutionResult
from .exceptions import ProviderNotAvailable, ProviderTimeoutError, ResponseParseError


class CLIProvider(LLMProvider):
    """Base class for CLI-based providers"""

    def __init__(self, cli_command: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize CLI provider

        Args:
            cli_command: Command to execute
            config: Additional configuration
        """
        super().__init__(config)
        self.cli_command = cli_command
        self.timeout = config.get("timeout", 60) if config else 60

        # Verify command exists
        self._verify_command()

    def _verify_command(self):
        """Verify that the CLI command is available"""
        try:
            # Check if command exists
            cmd_parts = shlex.split(self.cli_command)
            if not cmd_parts:
                raise ProviderNotAvailable(
                    message="Empty CLI command",
                    provider=self.provider_name
                )

            # Try to find the command
            result = subprocess.run(
                ["which", cmd_parts[0]],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                raise ProviderNotAvailable(
                    message=f"Command not found: {cmd_parts[0]}",
                    provider=self.provider_name,
                    details={"command": cmd_parts[0]}
                )

        except subprocess.TimeoutExpired:
            raise ProviderNotAvailable(
                message=f"Timeout checking command: {self.cli_command}",
                provider=self.provider_name
            )
        except Exception as e:
            if isinstance(e, ProviderNotAvailable):
                raise
            raise ProviderNotAvailable(
                message=f"Failed to verify command: {e}",
                provider=self.provider_name,
                details={"error": str(e)}
            )

    def _build_command(self, system_prompt: str, user_prompt: str, **kwargs) -> list:
        """
        Build the CLI command with prompts

        Args:
            system_prompt: System instructions
            user_prompt: User message
            **kwargs: Additional parameters

        Returns:
            Command parts as list
        """
        # Default implementation - subclasses should override
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        return shlex.split(self.cli_command) + [combined_prompt]

    def _execute_command(self, command: list) -> CLIExecutionResult:
        """
        Execute CLI command and capture output

        Args:
            command: Command parts as list

        Returns:
            CLIExecutionResult with output
        """
        start_time = time.time()

        try:
            logger.debug(f"Executing command: {' '.join(command[:2])}...")  # Log only first parts for security

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            )

            duration = time.time() - start_time

            return CLIExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                duration=duration
            )

        except subprocess.TimeoutExpired as e:
            raise ProviderTimeoutError(
                message=f"CLI command timed out after {self.timeout} seconds",
                provider=self.provider_name,
                details={"timeout": self.timeout}
            )
        except Exception as e:
            logger.error(f"CLI execution error: {e}")
            raise

    def _parse_cli_output(self, result: CLIExecutionResult) -> str:
        """
        Parse CLI output to extract response

        Args:
            result: CLI execution result

        Returns:
            Parsed response text
        """
        # Default implementation - subclasses can override
        if result.return_code != 0:
            logger.error(f"CLI command failed: {result.stderr}")
            raise ResponseParseError(
                message=f"CLI command failed with code {result.return_code}",
                provider=self.provider_name,
                details={"stderr": result.stderr}
            )

        return result.stdout.strip()

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Generate completion via CLI command

        Args:
            system_prompt: System instructions
            user_prompt: User message
            temperature: Sampling temperature (may be ignored)
            max_tokens: Maximum tokens (may be ignored)

        Returns:
            Dict containing response and metadata
        """
        # Build command
        command = self._build_command(
            system_prompt,
            user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Execute command
        result = self._execute_command(command)

        # Parse output
        raw_content = self._parse_cli_output(result)

        # Parse JSON from response
        content = self.parse_response(raw_content)

        return {
            "content": content,
            "raw_content": raw_content,
            "tokens_used": self.estimate_tokens(raw_content),
            "model": "cli",
            "duration": result.duration,
            "provider": self.provider_name
        }