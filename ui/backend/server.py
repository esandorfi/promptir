"""FastAPI server for promptir UI."""

from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import Settings, get_settings, get_session_by_id
from .routes import api_router
from .schemas import DiffResponse
from .services.diff_service import compute_diff

app = FastAPI(
    title="promptir Workbench",
    description="UI for managing prompt manifests",
    version="0.1.0",
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


# Diff endpoint (needs access to services)
@app.get("/api/sessions/{session_id}/prompts/{prompt_id}/diff", response_model=DiffResponse)
def get_diff(
    session_id: str,
    prompt_id: str,
    v1: str,
    v2: str,
    settings: Settings = Depends(get_settings),
) -> DiffResponse:
    """Get diff between two versions of a prompt."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    result = compute_diff(session.prompts_dir, prompt_id, v1, v2)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Could not compute diff for {prompt_id}"
        )

    frontmatter_diff, template_diff = result
    return DiffResponse(
        prompt_id=prompt_id,
        version1=v1,
        version2=v2,
        frontmatter_diff=frontmatter_diff,
        template_diff=template_diff,
    )


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Mount static files for production (frontend build)
# This should be last to not override API routes
static_path = Path(__file__).parent.parent / "frontend" / "dist"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
