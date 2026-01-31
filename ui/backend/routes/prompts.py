"""Prompt CRUD endpoints."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..config import Settings, get_session_by_id, get_settings
from ..schemas import (
    BlockSpec,
    PromptCreateRequest,
    PromptDetail,
    PromptListResponse,
    PromptMessage,
    PromptSource,
    PromptSummary,
    PromptUpdateRequest,
)
from ..services.prompt_service import (
    get_includes,
    list_prompt_files,
    load_manifest,
    load_prompt_source,
    save_prompt_source,
)

router = APIRouter()


@router.get("/api/sessions/{session_id}/prompts", response_model=PromptListResponse)
def list_prompts(session_id: str, settings: Settings = Depends(get_settings)) -> PromptListResponse:
    """List all prompts in a session."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    manifest = load_manifest(session.manifest_path)
    if not manifest:
        # Fallback to listing files if no manifest
        prompts = list_prompt_files(session.prompts_dir)
        includes = get_includes(session.prompts_dir)
    else:
        prompts = [
            PromptSummary(
                id=p["id"],
                version=p["version"],
                template_engine=p.get("template_engine", "simple"),
                metadata=p.get("metadata", {}),
                variables=[v for v in p.get("variables", []) if not v.startswith("_")],
                blocks={k: BlockSpec(**v) for k, v in p.get("blocks", {}).items()},
            )
            for p in manifest.get("prompts", [])
        ]
        includes = get_includes(session.prompts_dir)

    return PromptListResponse(prompts=prompts, includes=includes)


@router.get("/api/sessions/{session_id}/prompts/{prompt_id}")
def get_prompt_latest(
    session_id: str, prompt_id: str, settings: Settings = Depends(get_settings)
) -> PromptDetail:
    """Get the latest version of a prompt."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    manifest = load_manifest(session.manifest_path)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")

    # Find latest version
    versions = [p for p in manifest.get("prompts", []) if p["id"] == prompt_id]
    if not versions:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")

    # Sort by version and get latest
    versions.sort(key=lambda x: x["version"], reverse=True)
    prompt = versions[0]

    return _prompt_to_detail(prompt)


@router.get("/api/sessions/{session_id}/prompts/{prompt_id}/{version}")
def get_prompt_version(
    session_id: str,
    prompt_id: str,
    version: str,
    settings: Settings = Depends(get_settings),
) -> PromptDetail:
    """Get a specific version of a prompt."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    manifest = load_manifest(session.manifest_path)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")

    prompt = next(
        (
            p
            for p in manifest.get("prompts", [])
            if p["id"] == prompt_id and p["version"] == version
        ),
        None,
    )
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}@{version}")

    return _prompt_to_detail(prompt)


@router.get("/api/sessions/{session_id}/prompts/{prompt_id}/{version}/source")
def get_prompt_source(
    session_id: str,
    prompt_id: str,
    version: str,
    settings: Settings = Depends(get_settings),
) -> PromptSource:
    """Get the raw source file of a prompt."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    source = load_prompt_source(session.prompts_dir, prompt_id, version)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source not found: {prompt_id}@{version}")

    return source


@router.put("/api/sessions/{session_id}/prompts/{prompt_id}/{version}")
def update_prompt(
    session_id: str,
    prompt_id: str,
    version: str,
    request: PromptUpdateRequest,
    settings: Settings = Depends(get_settings),
) -> PromptSource:
    """Update a prompt source file."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    result = save_prompt_source(session.prompts_dir, prompt_id, version, request.content)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to save prompt")

    return result


@router.post("/api/sessions/{session_id}/prompts")
def create_prompt(
    session_id: str,
    request: PromptCreateRequest,
    settings: Settings = Depends(get_settings),
) -> PromptSource:
    """Create a new prompt."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    # Check if prompt already exists
    existing = load_prompt_source(session.prompts_dir, request.id, request.version)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Prompt already exists: {request.id}@{request.version}",
        )

    result = save_prompt_source(session.prompts_dir, request.id, request.version, request.content)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create prompt")

    return result


@router.delete("/api/sessions/{session_id}/prompts/{prompt_id}/{version}")
def delete_prompt(
    session_id: str,
    prompt_id: str,
    version: str,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Delete a prompt version."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    prompts_dir = Path(session.prompts_dir)
    prompt_path = prompts_dir / prompt_id / f"{version}.md"

    if not prompt_path.exists():
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}@{version}")

    prompt_path.unlink()

    # Remove directory if empty
    prompt_dir = prompts_dir / prompt_id
    if prompt_dir.exists() and not list(prompt_dir.iterdir()):
        prompt_dir.rmdir()

    return {"deleted": True, "prompt_id": prompt_id, "version": version}


def _prompt_to_detail(prompt: dict) -> PromptDetail:
    """Convert manifest prompt dict to PromptDetail."""
    return PromptDetail(
        id=prompt["id"],
        version=prompt["version"],
        template_engine=prompt.get("template_engine", "simple"),
        metadata=prompt.get("metadata", {}),
        variables=[v for v in prompt.get("variables", []) if not v.startswith("_")],
        blocks={k: BlockSpec(**v) for k, v in prompt.get("blocks", {}).items()},
        messages=[PromptMessage(**m) for m in prompt.get("messages", [])],
        hash=prompt.get("hash", ""),
    )
