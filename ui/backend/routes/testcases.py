"""Test case management endpoints."""

import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..config import Settings, get_session_by_id, get_settings
from ..schemas import (
    TestCase,
    TestCaseCreateRequest,
    TestCaseListResponse,
    TestCaseUpdateRequest,
)

router = APIRouter()


def _get_testcases_path(settings: Settings, session_id: str, prompt_id: str, version: str) -> Path:
    """Get path to test cases file."""
    return Path(settings.testcases_dir) / session_id / f"{prompt_id}_{version}.json"


def _load_testcases(path: Path) -> dict:
    """Load test cases from file."""
    if not path.exists():
        return {"prompt_id": "", "version": "", "test_cases": []}
    with open(path) as f:
        return json.load(f)


def _save_testcases(path: Path, data: dict) -> None:
    """Save test cases to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


@router.get(
    "/api/sessions/{session_id}/prompts/{prompt_id}/{version}/testcases",
    response_model=TestCaseListResponse,
)
def list_testcases(
    session_id: str,
    prompt_id: str,
    version: str,
    settings: Settings = Depends(get_settings),
) -> TestCaseListResponse:
    """List test cases for a prompt."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    path = _get_testcases_path(settings, session_id, prompt_id, version)
    data = _load_testcases(path)

    return TestCaseListResponse(
        prompt_id=prompt_id,
        version=version,
        test_cases=[TestCase(**tc) for tc in data.get("test_cases", [])],
    )


@router.post(
    "/api/sessions/{session_id}/prompts/{prompt_id}/{version}/testcases",
    response_model=TestCase,
)
def create_testcase(
    session_id: str,
    prompt_id: str,
    version: str,
    request: TestCaseCreateRequest,
    settings: Settings = Depends(get_settings),
) -> TestCase:
    """Create a new test case."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    path = _get_testcases_path(settings, session_id, prompt_id, version)
    data = _load_testcases(path)

    if not data.get("prompt_id"):
        data["prompt_id"] = prompt_id
        data["version"] = version

    testcase = TestCase(
        id=f"tc-{uuid.uuid4().hex[:8]}",
        name=request.name,
        created_at=datetime.utcnow().isoformat() + "Z",
        inputs=request.inputs,
        last_response=None,
    )

    data["test_cases"].append(testcase.model_dump())
    _save_testcases(path, data)

    return testcase


@router.put(
    "/api/sessions/{session_id}/prompts/{prompt_id}/{version}/testcases/{testcase_id}",
    response_model=TestCase,
)
def update_testcase(
    session_id: str,
    prompt_id: str,
    version: str,
    testcase_id: str,
    request: TestCaseUpdateRequest,
    settings: Settings = Depends(get_settings),
) -> TestCase:
    """Update a test case."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    path = _get_testcases_path(settings, session_id, prompt_id, version)
    data = _load_testcases(path)

    testcases = data.get("test_cases", [])
    tc_index = next((i for i, tc in enumerate(testcases) if tc["id"] == testcase_id), None)

    if tc_index is None:
        raise HTTPException(status_code=404, detail=f"Test case not found: {testcase_id}")

    tc = testcases[tc_index]
    if request.name is not None:
        tc["name"] = request.name
    if request.inputs is not None:
        tc["inputs"] = request.inputs.model_dump()
    if request.last_response is not None:
        tc["last_response"] = request.last_response.model_dump()

    testcases[tc_index] = tc
    data["test_cases"] = testcases
    _save_testcases(path, data)

    return TestCase(**tc)


@router.delete("/api/sessions/{session_id}/prompts/{prompt_id}/{version}/testcases/{testcase_id}")
def delete_testcase(
    session_id: str,
    prompt_id: str,
    version: str,
    testcase_id: str,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Delete a test case."""
    session = get_session_by_id(settings, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    path = _get_testcases_path(settings, session_id, prompt_id, version)
    data = _load_testcases(path)

    testcases = data.get("test_cases", [])
    original_count = len(testcases)
    testcases = [tc for tc in testcases if tc["id"] != testcase_id]

    if len(testcases) == original_count:
        raise HTTPException(status_code=404, detail=f"Test case not found: {testcase_id}")

    data["test_cases"] = testcases
    _save_testcases(path, data)

    return {"deleted": True, "testcase_id": testcase_id}
