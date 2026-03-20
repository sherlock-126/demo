"""
Tests for the CLI module
"""

import pytest
from unittest.mock import patch, Mock
from click.testing import CliRunner
from content_generator.cli import cli


class TestCLI:
    """Test CLI commands"""

    def test_cli_version(self):
        """Test version command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    @patch('content_generator.cli.ScriptGenerator')
    @patch('content_generator.cli.config')
    def test_generate_command_no_api_key(self, mock_config, mock_generator):
        """Test generate command without API key"""
        mock_config.openai_api_key = None

        runner = CliRunner()
        result = runner.invoke(cli, ['generate', 'Test topic'])

        assert result.exit_code == 1
        assert "API key not found" in result.output

    @patch('content_generator.cli.ScriptGenerator')
    @patch('content_generator.cli.config')
    def test_generate_command_success(self, mock_config, mock_generator):
        """Test successful generate command"""
        mock_config.openai_api_key = "test-key"

        mock_script = Mock()
        mock_script.topic = "Test topic"
        mock_script.main_title = "Test Title"
        mock_script.slides = [Mock()]

        mock_gen_instance = Mock()
        mock_generator.return_value = mock_gen_instance
        mock_gen_instance.generate.return_value = mock_script
        mock_gen_instance.export_script.return_value = '{"topic": "Test"}'

        runner = CliRunner()
        result = runner.invoke(cli, ['generate', 'Test topic'])

        assert result.exit_code == 0
        assert "Successfully generated" in result.output

    @patch('content_generator.cli.ScriptGenerator')
    @patch('content_generator.cli.config')
    def test_list_command(self, mock_config, mock_generator):
        """Test list command"""
        mock_config.openai_api_key = "test-key"

        mock_gen_instance = Mock()
        mock_generator.return_value = mock_gen_instance
        mock_gen_instance.list_scripts.return_value = [
            {
                "filename": "test.json",
                "topic": "Test Topic",
                "num_slides": 3,
                "generated_at": "2024-03-20"
            }
        ]

        runner = CliRunner()
        result = runner.invoke(cli, ['list'])

        assert result.exit_code == 0
        assert "test.json" in result.output or "Generated Scripts" in result.output

    @patch('content_generator.cli.config')
    def test_setup_command(self, mock_config):
        """Test setup command"""
        mock_config.openai_api_key = "test-key"
        mock_config.data_dir = "/data"
        mock_config.scripts_dir = "/data/scripts"
        mock_config.logs_dir = "/data/logs"
        mock_config.validate.return_value = True

        runner = CliRunner()
        result = runner.invoke(cli, ['setup'])

        assert result.exit_code == 0
        assert "API key found" in result.output
        assert "Configuration is valid" in result.output