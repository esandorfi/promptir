from __future__ import annotations

import json
from pathlib import Path

import pytest

from promptir.compiler import compile_prompts
from promptir.errors import PromptCompileError


def _write_prompt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_compile_success_with_include(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    include_path = src_root / "_includes" / "policy" / "v1.md"
    _write_prompt(
        include_path,
        """---
{
  "id": "policy",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Follow policy.
""",
    )
    prompt_path = src_root / "planner" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "planner",
  "version": "v1",
  "metadata": {},
  "variables": ["question"],
  "includes": ["policy@v1"],
  "blocks": {
    "_context": {"optional": true, "default": ""}
  }
}
---
# system
Plan carefully.

# user
Question: {{question}}
Context: {{_context}}
""",
    )
    out_path = tmp_path / "dist" / "manifest.json"
    manifest = compile_prompts(str(src_root), str(out_path))
    assert manifest["schema_version"] == 1
    assert len(manifest["prompts"]) == 1

    data = json.loads(out_path.read_text(encoding="utf-8"))
    prompt = data["prompts"][0]
    assert prompt["id"] == "planner"
    assert prompt["template_engine"] == "simple"
    assert "hash" in prompt
    assert "Follow policy" in prompt["messages"][0]["content"]


def test_compile_invalid_variable_name(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "bad" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "bad",
  "version": "v1",
  "metadata": {},
  "variables": ["BadName"]
}
---
# system
Bad.

# user
{{BadName}}
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid variable name"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_compile_undeclared_variable(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "bad" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "bad",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Bad.

# user
{{missing}}
""",
    )
    with pytest.raises(PromptCompileError, match="Undeclared names"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_compile_missing_role(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "bad" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "bad",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Only system.
""",
    )
    with pytest.raises(PromptCompileError, match="Missing required roles"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_compile_invalid_template_engine(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "bad" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "bad",
  "version": "v1",
  "template_engine": "unknown",
  "metadata": {},
  "variables": []
}
---
# system
Bad.

# user
Hi.
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid template_engine"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))
