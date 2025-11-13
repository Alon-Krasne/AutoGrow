"""Tests for agentic workflow"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Mock environment variables before importing
os.environ['GITHUB_TOKEN'] = 'test_token'
os.environ['ANTHROPIC_API_KEY'] = 'test_key'
os.environ['REPO_URL'] = 'https://github.com/test/repo'

from agentic_workflow import AgenticWorkflow
from config import AgentConfig


class TestAgenticWorkflow:
    """Test suite for AgenticWorkflow"""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing"""
        config = Mock(spec=AgentConfig)
        config.github_token = 'test_token'
        config.anthropic_api_key = 'test_key'
        config.repo_url = 'https://github.com/test/repo'
        config.workspace_path = '/tmp/test_workspace'
        config.agent_mode = 'autonomous'
        config.prompt_template = 'default'
        config.custom_prompt_path = None
        config.validate = Mock()
        return config
    
    @pytest.fixture
    def workflow(self, mock_config):
        """Create a workflow instance for testing"""
        with patch('agentic_workflow.Github'), \
             patch('agentic_workflow.Anthropic'), \
             patch('agentic_workflow.setup_logger'):
            return AgenticWorkflow(config=mock_config)
    
    def test_initialization(self, workflow, mock_config):
        """Test workflow initialization"""
        assert workflow.config == mock_config
        assert workflow.config.github_token == 'test_token'
        assert workflow.config.anthropic_api_key == 'test_key'
    
    def test_parse_repo_info(self, workflow):
        """Test repository URL parsing"""
        owner, repo = workflow._parse_repo_info()
        assert owner == 'test'
        assert repo == 'repo'
    
    def test_parse_repo_info_with_git_suffix(self, mock_config):
        """Test parsing URL with .git suffix"""
        mock_config.repo_url = 'https://github.com/owner/name.git'
        with patch('agentic_workflow.Github'), \
             patch('agentic_workflow.Anthropic'), \
             patch('agentic_workflow.setup_logger'):
            workflow = AgenticWorkflow(config=mock_config)
            owner, repo = workflow._parse_repo_info()
            assert owner == 'owner'
            assert repo == 'name'
    
    def test_parse_repo_info_invalid_url(self, mock_config):
        """Test parsing invalid URL"""
        mock_config.repo_url = 'https://github.com/invalid'
        with patch('agentic_workflow.Github'), \
             patch('agentic_workflow.Anthropic'), \
             patch('agentic_workflow.setup_logger'):
            workflow = AgenticWorkflow(config=mock_config)
            with pytest.raises(ValueError, match="Invalid repository URL"):
                workflow._parse_repo_info()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
