"""Pytest fixtures for backend tests."""

import json
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.server import app
from backend.config import Settings, get_settings


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_prompt_content():
    """Sample prompt content for testing."""
    return '''---
{
  "id": "test_prompt",
  "version": "v1",
  "metadata": {"owner": "test"},
  "variables": ["question", "context"],
  "blocks": {
    "_rag_context": {"optional": true, "default": ""}
  },
  "template_engine": "simple"
}
---
# system
You are a helpful assistant.

# user
Question: {{question}}
Context: {{context}}
RAG: {{_rag_context}}
'''


@pytest.fixture
def sample_session_config(temp_dir, sample_prompt_content):
    """Create a sample session configuration."""
    # Create prompts directory
    prompts_dir = temp_dir / "prompts"
    prompt_dir = prompts_dir / "test_prompt"
    prompt_dir.mkdir(parents=True)

    # Write sample prompt
    (prompt_dir / "v1.md").write_text(sample_prompt_content)

    # Create manifest
    manifest_path = temp_dir / "manifest.json"

    # Create sessions config
    sessions_path = temp_dir / "sessions.json"
    sessions_path.write_text(json.dumps({
        "sessions": [{
            "id": "test-session",
            "name": "Test Session",
            "manifest_path": str(manifest_path),
            "prompts_dir": str(prompts_dir)
        }]
    }))

    # Create testcases dir
    testcases_dir = temp_dir / "testcases"
    testcases_dir.mkdir()

    return {
        "sessions_path": str(sessions_path),
        "prompts_dir": str(prompts_dir),
        "manifest_path": str(manifest_path),
        "testcases_dir": str(testcases_dir),
    }


@pytest.fixture
def test_settings(sample_session_config):
    """Create test settings."""
    return Settings(
        openai_api_key="test-key",
        openai_base_url="https://api.openai.com/v1",
        sessions_path=sample_session_config["sessions_path"],
        testcases_dir=sample_session_config["testcases_dir"],
    )


@pytest.fixture
def client(test_settings):
    """Create a test client with overridden settings."""
    def override_settings():
        return test_settings

    app.dependency_overrides[get_settings] = override_settings

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
