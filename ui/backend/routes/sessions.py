"""Session management endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from ..config import Settings, get_session_by_id, get_settings, load_sessions
from ..schemas import SessionListResponse, SessionResponse

router = APIRouter()


@router.get("/api/sessions", response_model=SessionListResponse)
def list_sessions(settings: Settings = Depends(get_settings)) -> SessionListResponse:
    """List all available sessions."""
    sessions = load_sessions(settings)
    return SessionListResponse(
        sessions=[
            SessionResponse(
                id=s.id,
                name=s.name,
                manifest_path=s.manifest_path,
                prompts_dir=s.prompts_dir,
            )
            for s in sessions
        ]
    )


@router.get("/api/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, settings: Settings = Depends(get_settings)) -> SessionResponse:
    """Get a specific session by ID."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    return SessionResponse(
        id=session.id,
        name=session.name,
        manifest_path=session.manifest_path,
        prompts_dir=session.prompts_dir,
    )
