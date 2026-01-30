"""Compilation and rendering endpoints."""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends

# Add parent to path to import promptir
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from promptir import compile_prompts, PromptRegistry
from promptir.errors import PromptCompileError, PromptInputError

from ..config import Settings, get_settings, get_session_by_id
from ..schemas import (
    CompileResult,
    ValidationResult,
    ValidationError,
    ValidationWarning,
    RenderRequest,
    RenderResponse,
    PromptMessage,
)

router = APIRouter()


@router.post("/api/sessions/{session_id}/compile", response_model=CompileResult)
def compile_session(
    session_id: str, settings: Settings = Depends(get_settings)
) -> CompileResult:
    """Compile all prompts in a session."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    try:
        result = compile_prompts(session.prompts_dir, session.manifest_path)
        return CompileResult(
            success=True,
            manifest_path=session.manifest_path,
            errors=[],
            prompts_compiled=len(result.get("prompts", [])),
        )
    except PromptCompileError as e:
        return CompileResult(
            success=False,
            manifest_path=None,
            errors=[ValidationError(type="compile", message=str(e))],
            prompts_compiled=0,
        )
    except Exception as e:
        return CompileResult(
            success=False,
            manifest_path=None,
            errors=[ValidationError(type="error", message=str(e))],
            prompts_compiled=0,
        )


@router.post("/api/sessions/{session_id}/validate", response_model=ValidationResult)
def validate_session(
    session_id: str, settings: Settings = Depends(get_settings)
) -> ValidationResult:
    """Validate prompts without writing manifest."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    try:
        # Compile to a temp path to validate
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as f:
            compile_prompts(session.prompts_dir, f.name)
        return ValidationResult(valid=True, errors=[], warnings=warnings)
    except PromptCompileError as e:
        errors.append(ValidationError(type="compile", message=str(e)))
        return ValidationResult(valid=False, errors=errors, warnings=warnings)
    except Exception as e:
        errors.append(ValidationError(type="error", message=str(e)))
        return ValidationResult(valid=False, errors=errors, warnings=warnings)


@router.post("/api/sessions/{session_id}/render", response_model=RenderResponse)
def render_prompt(
    session_id: str,
    request: RenderRequest,
    settings: Settings = Depends(get_settings),
) -> RenderResponse:
    """Render a prompt with given inputs."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    manifest_path = Path(session.manifest_path)
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="Manifest not found. Compile first.")

    try:
        registry = PromptRegistry.from_manifest_path(str(manifest_path))
        rendered = registry.render(
            request.prompt_id,
            version=request.version,
            vars=request.vars,
            blocks=request.blocks,
        )

        messages = [
            PromptMessage(role=m.role, content=m.content) for m in rendered.messages
        ]

        # Estimate tokens (rough: ~4 chars per token)
        total_chars = sum(len(m.content) for m in messages)
        token_estimate = total_chars // 4

        return RenderResponse(messages=messages, token_estimate=token_estimate)

    except PromptInputError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
