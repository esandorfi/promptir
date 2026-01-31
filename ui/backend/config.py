"""Configuration management for promptir UI."""

import json
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class SessionConfig(BaseModel):
    """Configuration for a single session."""

    id: str
    name: str
    manifest_path: str
    prompts_dir: str


class Settings(BaseSettings):
    """Application settings."""

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    sessions_path: str = "ui/data/sessions.json"
    testcases_dir: str = "ui/data/testcases"

    # Hardcoded model list
    available_models: list[str] = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
    ]

    class Config:
        env_prefix = "PROMPTIR_"
        env_file = ".env"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def load_sessions(settings: Settings) -> list[SessionConfig]:
    """Load session configurations from file."""
    sessions_path = Path(settings.sessions_path)

    if not sessions_path.exists():
        return []

    with open(sessions_path) as f:
        data = json.load(f)

    return [SessionConfig(**s) for s in data.get("sessions", [])]


def get_session_by_id(settings: Settings, session_id: str) -> SessionConfig | None:
    """Get a specific session by ID."""
    sessions = load_sessions(settings)
    for session in sessions:
        if session.id == session_id:
            return session
    return None
