"""Integration tests for API endpoints using demo datasets."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src to path for promptir imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from backend.config import Settings, get_settings
from backend.server import app


@pytest.fixture
def demo_settings():
    """Settings using actual demo datasets."""
    # Use actual demo datasets for integration tests
    base_path = Path(__file__).parent.parent.parent.parent

    # Check if demo datasets exist
    demo_manifest = base_path / "data" / "demo_datasets" / "document_analysis" / "manifest.json"
    if not demo_manifest.exists():
        pytest.skip("Demo datasets not compiled. Run: python scripts/compile_demo_datasets.py")

    return Settings(
        openai_api_key="",  # Not needed for non-inference tests
        sessions_path=str(base_path / "ui" / "data" / "sessions.json"),
        testcases_dir=str(base_path / "ui" / "data" / "testcases"),
    )


@pytest.fixture
def demo_client(demo_settings):
    """Test client with demo settings."""
    def override_settings():
        return demo_settings

    app.dependency_overrides[get_settings] = override_settings

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestSessionsAPI:
    """Integration tests for sessions endpoints."""

    def test_list_sessions(self, demo_client):
        """Should list configured sessions."""
        response = demo_client.get("/api/sessions")
        assert response.status_code == 200

        data = response.json()
        assert "sessions" in data
        assert len(data["sessions"]) >= 2  # At least demo-docs and demo-local

        session_ids = {s["id"] for s in data["sessions"]}
        assert "demo-docs" in session_ids

    def test_get_session(self, demo_client):
        """Should get specific session."""
        response = demo_client.get("/api/sessions/demo-docs")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "demo-docs"
        assert data["name"] == "Document Analysis"

    def test_get_nonexistent_session(self, demo_client):
        """Should return 404 for nonexistent session."""
        response = demo_client.get("/api/sessions/nonexistent")
        assert response.status_code == 404


class TestPromptsAPI:
    """Integration tests for prompts endpoints."""

    def test_list_prompts(self, demo_client):
        """Should list prompts in session."""
        response = demo_client.get("/api/sessions/demo-docs/prompts")
        assert response.status_code == 200

        data = response.json()
        assert "prompts" in data
        assert len(data["prompts"]) >= 1

        # Check prompt structure
        prompt = data["prompts"][0]
        assert "id" in prompt
        assert "version" in prompt
        assert "variables" in prompt

    def test_get_prompt_detail(self, demo_client):
        """Should get prompt details."""
        # First get list to find a prompt ID
        list_response = demo_client.get("/api/sessions/demo-docs/prompts")
        prompts = list_response.json()["prompts"]
        if not prompts:
            pytest.skip("No prompts in demo-docs session")

        prompt_id = prompts[0]["id"]
        version = prompts[0]["version"]

        response = demo_client.get(f"/api/sessions/demo-docs/prompts/{prompt_id}/{version}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == prompt_id
        assert "messages" in data
        assert len(data["messages"]) >= 1

    def test_get_prompt_source(self, demo_client):
        """Should get raw prompt source."""
        list_response = demo_client.get("/api/sessions/demo-docs/prompts")
        prompts = list_response.json()["prompts"]
        if not prompts:
            pytest.skip("No prompts in demo-docs session")

        prompt_id = prompts[0]["id"]
        version = prompts[0]["version"]

        response = demo_client.get(f"/api/sessions/demo-docs/prompts/{prompt_id}/{version}/source")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == prompt_id
        assert "content" in data
        assert "---" in data["content"]  # Has frontmatter


class TestValidationAPI:
    """Integration tests for validation endpoint."""

    def test_validate_session(self, demo_client):
        """Should validate session prompts."""
        response = demo_client.post("/api/sessions/demo-docs/validate")
        assert response.status_code == 200

        data = response.json()
        assert "valid" in data
        # Demo datasets should be valid
        assert data["valid"] is True


class TestRenderAPI:
    """Integration tests for render endpoint."""

    def test_render_prompt(self, demo_client):
        """Should render prompt with inputs."""
        # Get a prompt to render
        list_response = demo_client.get("/api/sessions/demo-docs/prompts")
        prompts = list_response.json()["prompts"]
        if not prompts:
            pytest.skip("No prompts in demo-docs session")

        prompt = prompts[0]

        # Build minimal inputs
        vars_input = {v: f"test_{v}" for v in prompt["variables"]}
        blocks_input = {b: "" for b in prompt["blocks"]}

        response = demo_client.post(
            "/api/sessions/demo-docs/render",
            json={
                "prompt_id": prompt["id"],
                "version": prompt["version"],
                "vars": vars_input,
                "blocks": blocks_input,
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert "messages" in data
        assert "token_estimate" in data
        assert len(data["messages"]) >= 1


class TestModelsAPI:
    """Integration tests for models endpoint."""

    def test_list_models(self, demo_client):
        """Should list available models."""
        response = demo_client.get("/api/infer/models")
        assert response.status_code == 200

        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
        assert "gpt-4o" in data["models"]


class TestHealthAPI:
    """Integration tests for health endpoint."""

    def test_health_check(self, demo_client):
        """Should return healthy status."""
        response = demo_client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
