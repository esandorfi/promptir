"""Tests for configuration logic."""

import json
import pytest
from backend.config import (
    Settings,
    SessionConfig,
    load_sessions,
    get_session_by_id,
)


class TestSettings:
    """Tests for Settings class."""

    def test_default_settings(self):
        """Should have sensible defaults."""
        settings = Settings()
        assert settings.openai_base_url == "https://api.openai.com/v1"
        assert len(settings.available_models) > 0
        assert "gpt-4o" in settings.available_models

    def test_custom_settings(self):
        """Should accept custom values."""
        settings = Settings(
            openai_api_key="test-key",
            openai_base_url="http://localhost:8080",
        )
        assert settings.openai_api_key == "test-key"
        assert settings.openai_base_url == "http://localhost:8080"


class TestLoadSessions:
    """Tests for load_sessions function."""

    def test_load_valid_sessions(self, temp_dir):
        """Should load sessions from JSON file."""
        sessions_path = temp_dir / "sessions.json"
        sessions_path.write_text(json.dumps({
            "sessions": [
                {
                    "id": "session-1",
                    "name": "Session One",
                    "manifest_path": "/path/to/manifest.json",
                    "prompts_dir": "/path/to/prompts"
                },
                {
                    "id": "session-2",
                    "name": "Session Two",
                    "manifest_path": "/path/to/manifest2.json",
                    "prompts_dir": "/path/to/prompts2"
                }
            ]
        }))

        settings = Settings(sessions_path=str(sessions_path))
        sessions = load_sessions(settings)

        assert len(sessions) == 2
        assert sessions[0].id == "session-1"
        assert sessions[1].name == "Session Two"

    def test_load_nonexistent_file(self, temp_dir):
        """Should return empty list for nonexistent file."""
        settings = Settings(sessions_path=str(temp_dir / "nonexistent.json"))
        sessions = load_sessions(settings)
        assert sessions == []

    def test_load_empty_sessions(self, temp_dir):
        """Should handle empty sessions array."""
        sessions_path = temp_dir / "sessions.json"
        sessions_path.write_text(json.dumps({"sessions": []}))

        settings = Settings(sessions_path=str(sessions_path))
        sessions = load_sessions(settings)
        assert sessions == []


class TestGetSessionById:
    """Tests for get_session_by_id function."""

    def test_get_existing_session(self, temp_dir):
        """Should find session by ID."""
        sessions_path = temp_dir / "sessions.json"
        sessions_path.write_text(json.dumps({
            "sessions": [
                {"id": "target", "name": "Target", "manifest_path": "/m", "prompts_dir": "/p"}
            ]
        }))

        settings = Settings(sessions_path=str(sessions_path))
        session = get_session_by_id(settings, "target")

        assert session is not None
        assert session.id == "target"
        assert session.name == "Target"

    def test_get_nonexistent_session(self, temp_dir):
        """Should return None for nonexistent session."""
        sessions_path = temp_dir / "sessions.json"
        sessions_path.write_text(json.dumps({"sessions": []}))

        settings = Settings(sessions_path=str(sessions_path))
        session = get_session_by_id(settings, "nonexistent")

        assert session is None
