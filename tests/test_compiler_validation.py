from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from promptir.compiler import (
    _build_messages,
    _merge_role_content,
    _validate_blocks,
    _validate_declared_names,
    _validate_path_consistency,
    _validate_used_names,
    _validate_variables,
    compile_prompts,
)
from promptir.errors import PromptCompileError
from promptir.models import BlockSpec


def _write_prompt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _new_root(tmp_path: Path, name: str) -> Path:
    return tmp_path / name / "src" / "llm" / "prompts"


def test_compile_missing_source_root(tmp_path: Path) -> None:
    with pytest.raises(PromptCompileError, match="Source root not found"):
        compile_prompts(str(tmp_path / "missing"), str(tmp_path / "out.json"))


def test_duplicate_prompt_detection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src_root = _new_root(tmp_path, "duplicate")
    prompt_path = src_root / "dup" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "dup",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Hello
# user
Hi
""",
    )

    def duplicate_files(_src_root: Path) -> list[Path]:
        return [prompt_path, prompt_path]

    monkeypatch.setattr("promptir.compiler._collect_prompt_files", duplicate_files)
    with pytest.raises(PromptCompileError, match="Duplicate prompt id/version"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_invalid_frontmatter_delimiters(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "frontmatter-missing")
    bad_path = src_root / "bad" / "v1.md"
    _write_prompt(bad_path, "# system\nHello")
    with pytest.raises(PromptCompileError, match="Missing frontmatter delimiter"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_missing_closing_frontmatter(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "frontmatter-closing")
    bad_path = src_root / "bad" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{ "id": "bad", "version": "v1", "metadata": {}, "variables": [] }
# system
Hello
""",
    )
    with pytest.raises(PromptCompileError, match="Missing closing frontmatter"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_empty_frontmatter(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "frontmatter-empty")
    bad_path = src_root / "bad" / "v1.md"
    _write_prompt(
        bad_path,
        """---
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Empty frontmatter"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_invalid_json_frontmatter(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "frontmatter-json")
    bad_path = src_root / "bad" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{ "id": "bad", "version": "v1", }
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid JSON frontmatter"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_invalid_heading_and_preamble(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "preamble")
    bad_path = src_root / "bad" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
Preamble
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Content before first role heading"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-role")
    bad_path = src_root / "bad2" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad2",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# invalid
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid role heading"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-heading")
    bad_path = src_root / "bad3" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad3",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
## system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid heading"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_blank_line_before_heading_is_allowed(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "blank-line")
    prompt_path = src_root / "ok" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "ok",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
   
# system
Hello
# user
Hi
""",
    )
    compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_frontmatter_field_validation(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "missing-field")
    bad_path = src_root / "bad" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad",
  "version": "v1",
  "metadata": {}
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Missing frontmatter field"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-id")
    bad_path = src_root / "bad2" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid id"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-version")
    bad_path = src_root / "bad3" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad3",
  "version": "",
  "metadata": {},
  "variables": []
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid version"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-metadata")
    bad_path = src_root / "bad4" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad4",
  "version": "v1",
  "metadata": [],
  "variables": []
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid metadata"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-variables")
    bad_path = src_root / "bad5" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad5",
  "version": "v1",
  "metadata": {},
  "variables": {}
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid variables"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_path_consistency_and_includes(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "invalid-path")
    bad_path = src_root / "nested" / "bad" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid prompt path"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "mismatch")
    bad_path = src_root / "mismatch" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "other",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Prompt id/version mismatch"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "include-mismatch")
    include_path = src_root / "_includes" / "policy" / "v1.md"
    _write_prompt(
        include_path,
        """---
{
  "id": "wrong",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Policy
""",
    )
    prompt_path = src_root / "ok" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "ok",
  "version": "v1",
  "metadata": {},
  "variables": [],
  "includes": ["policy@v1"]
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Include id/version mismatch"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_include_reference_validation(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "include-invalid")
    prompt_path = src_root / "ok" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "ok",
  "version": "v1",
  "metadata": {},
  "variables": [],
  "includes": ["policy"]
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid include reference"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "include-missing")
    prompt_path = src_root / "ok2" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "ok2",
  "version": "v1",
  "metadata": {},
  "variables": [],
  "includes": ["missing@v1"]
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Missing include file"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))


def test_block_validation(tmp_path: Path) -> None:
    src_root = _new_root(tmp_path, "invalid-blocks")
    bad_path = src_root / "bad" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad",
  "version": "v1",
  "metadata": {},
  "variables": [],
  "blocks": []
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid blocks"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-block-name")
    bad_path = src_root / "bad2" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad2",
  "version": "v1",
  "metadata": {},
  "variables": [],
  "blocks": {"context": {"optional": true}}
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid block name"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-block-spec")
    bad_path = src_root / "bad3" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad3",
  "version": "v1",
  "metadata": {},
  "variables": [],
  "blocks": {"_context": []}
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid block spec"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-block-optional")
    bad_path = src_root / "bad4" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad4",
  "version": "v1",
  "metadata": {},
  "variables": [],
  "blocks": {"_context": {"optional": "yes"}}
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid optional flag"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    src_root = _new_root(tmp_path, "invalid-block-default")
    bad_path = src_root / "bad5" / "v1.md"
    _write_prompt(
        bad_path,
        """---
{
  "id": "bad5",
  "version": "v1",
  "metadata": {},
  "variables": [],
  "blocks": {"_context": {"default": 123}}
}
---
# system
Hello
# user
Hi
""",
    )
    with pytest.raises(PromptCompileError, match="Invalid default"):
        compile_prompts(str(src_root), str(tmp_path / "out.json"))

    none_blocks: dict[str, Any] = {
        "id": "ok",
        "version": "v1",
        "metadata": {},
        "variables": [],
        "blocks": None,
    }
    assert _validate_blocks(none_blocks, Path("prompt.md")) == {}


def test_overlap_and_usage_validation() -> None:
    with pytest.raises(PromptCompileError, match="Variables and blocks overlap"):
        _validate_declared_names(["name"], {"name": BlockSpec()}, Path("prompt.md"))

    with pytest.raises(PromptCompileError, match="Declared but unused"):
        _validate_used_names(set(), ["name"], {}, Path("prompt.md"))

    with pytest.raises(PromptCompileError, match="Underscore names"):
        _validate_used_names({"_missing"}, ["_missing"], {}, Path("prompt.md"))


def test_merge_and_messages_helpers() -> None:
    assert _merge_role_content("include", "existing") == "include\n\nexisting"
    assert _merge_role_content("include", "") == "include"

    messages = _build_messages({"system": "sys", "user": "user", "assistant": "assistant"})
    assert messages[-1].role == "assistant"


def test_variable_and_path_helpers() -> None:
    with pytest.raises(PromptCompileError, match="Invalid variables"):
        _validate_variables({"variables": "bad"}, Path("prompt.md"))

    with pytest.raises(PromptCompileError, match="Invalid include path"):
        _validate_path_consistency(
            {"id": "policy", "version": "v1"},
            Path("src/llm/prompts/policy/v1.md"),
            Path("src/llm/prompts"),
            is_include=True,
        )
