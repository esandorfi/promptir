"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel
from typing import Any


# Session schemas
class SessionResponse(BaseModel):
    """Session information."""

    id: str
    name: str
    manifest_path: str
    prompts_dir: str


class SessionListResponse(BaseModel):
    """List of sessions."""

    sessions: list[SessionResponse]


# Prompt schemas
class BlockSpec(BaseModel):
    """Block specification."""

    optional: bool = True
    default: str = ""


class PromptMessage(BaseModel):
    """A single message in a prompt."""

    role: str
    content: str


class PromptSummary(BaseModel):
    """Summary of a prompt for listing."""

    id: str
    version: str
    template_engine: str
    metadata: dict[str, Any]
    variables: list[str]
    blocks: dict[str, BlockSpec]


class PromptDetail(BaseModel):
    """Full prompt detail including messages."""

    id: str
    version: str
    template_engine: str
    metadata: dict[str, Any]
    variables: list[str]
    blocks: dict[str, BlockSpec]
    messages: list[PromptMessage]
    hash: str


class PromptSource(BaseModel):
    """Raw source file content."""

    id: str
    version: str
    content: str
    path: str


class PromptListResponse(BaseModel):
    """List of prompts."""

    prompts: list[PromptSummary]
    includes: list[PromptSummary]


# Update schemas
class PromptUpdateRequest(BaseModel):
    """Request to update a prompt source."""

    content: str


class PromptCreateRequest(BaseModel):
    """Request to create a new prompt."""

    id: str
    version: str
    content: str


# Compilation schemas
class ValidationError(BaseModel):
    """A single validation error."""

    type: str
    message: str
    line: int | None = None
    variable: str | None = None


class ValidationWarning(BaseModel):
    """A single validation warning."""

    type: str
    message: str
    variable: str | None = None


class ValidationResult(BaseModel):
    """Result of validation."""

    valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]


class CompileResult(BaseModel):
    """Result of compilation."""

    success: bool
    manifest_path: str | None = None
    errors: list[ValidationError]
    prompts_compiled: int = 0


# Render schemas
class RenderRequest(BaseModel):
    """Request to render a prompt."""

    prompt_id: str
    version: str | None = None
    vars: dict[str, str] = {}
    blocks: dict[str, str] = {}


class RenderResponse(BaseModel):
    """Rendered prompt messages."""

    messages: list[PromptMessage]
    token_estimate: int


# Inference schemas
class InferenceRequest(BaseModel):
    """Request to run LLM inference."""

    messages: list[PromptMessage]
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1024


class InferenceResponse(BaseModel):
    """LLM inference response."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_estimate: float | None = None


class ModelsResponse(BaseModel):
    """Available models."""

    models: list[str]


# Test case schemas
class TestCaseInput(BaseModel):
    """Inputs for a test case."""

    vars: dict[str, str]
    blocks: dict[str, str]


class TestCaseResponse(BaseModel):
    """Saved response from a test case run."""

    content: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    timestamp: str


class TestCase(BaseModel):
    """A single test case."""

    id: str
    name: str
    created_at: str
    inputs: TestCaseInput
    last_response: TestCaseResponse | None = None


class TestCaseListResponse(BaseModel):
    """List of test cases."""

    prompt_id: str
    version: str
    test_cases: list[TestCase]


class TestCaseCreateRequest(BaseModel):
    """Request to create a test case."""

    name: str
    inputs: TestCaseInput


class TestCaseUpdateRequest(BaseModel):
    """Request to update a test case."""

    name: str | None = None
    inputs: TestCaseInput | None = None
    last_response: TestCaseResponse | None = None


# Diff schemas
class DiffResponse(BaseModel):
    """Diff between two versions."""

    prompt_id: str
    version1: str
    version2: str
    frontmatter_diff: str
    template_diff: str
