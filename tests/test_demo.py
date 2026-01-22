from __future__ import annotations

import json
from pathlib import Path

import pytest

from promptir.compiler import compile_prompts
from promptir.demo import dump_demo_results, render_demo, write_demo_results


def _write_prompt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_manifest(tmp_path: Path) -> Path:
    src_root = tmp_path / "prompts"
    prompt_path = src_root / "hello" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "hello",
  "version": "v1",
  "metadata": {},
  "variables": ["name"],
  "blocks": {"_context": {"optional": true, "default": ""}}
}
---
# system
Hello {{name}}. Context: {{_context}}.

# user
Hi {{name}}.
""",
    )
    manifest_path = tmp_path / "manifest.json"
    compile_prompts(str(src_root), str(manifest_path))
    return manifest_path


def test_render_demo_outputs_messages(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    demo_data = [
        {
            "id": "hello",
            "version": "v1",
            "vars": {"name": "Ada"},
            "blocks": {"_context": "Test"},
        }
    ]
    data_path = tmp_path / "demo.json"
    data_path.write_text(json.dumps(demo_data), encoding="utf-8")

    results = render_demo(str(manifest_path), str(data_path))

    assert len(results) == 1
    assert results[0]["messages"][0]["content"] == "Hello Ada. Context: Test."
    assert results[0]["messages"][1]["content"] == "Hi Ada."


def test_render_demo_rejects_non_list_data(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    data_path = tmp_path / "demo.json"
    data_path.write_text(json.dumps({"id": "hello"}), encoding="utf-8")

    with pytest.raises(ValueError, match="Demo data must be a list"):
        render_demo(str(manifest_path), str(data_path))


def test_render_demo_rejects_missing_id(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    data_path = tmp_path / "demo.json"
    data_path.write_text(json.dumps([{"vars": {"name": "Ada"}}]), encoding="utf-8")

    with pytest.raises(ValueError, match="Demo entry 'id' must be a string"):
        render_demo(str(manifest_path), str(data_path))


def test_render_demo_rejects_bad_version_type(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    data_path = tmp_path / "demo.json"
    data_path.write_text(
        json.dumps([{"id": "hello", "version": 1, "vars": {"name": "Ada"}}]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="version' must be a string"):
        render_demo(str(manifest_path), str(data_path))


def test_render_demo_handles_none_blocks(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    data_path = tmp_path / "demo.json"
    data_path.write_text(
        json.dumps([{"id": "hello", "version": "v1", "vars": {"name": "Ada"}, "blocks": None}]),
        encoding="utf-8",
    )

    results = render_demo(str(manifest_path), str(data_path))

    assert results[0]["blocks"] == {}


def test_render_demo_rejects_bad_blocks_type(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    data_path = tmp_path / "demo.json"
    data_path.write_text(
        json.dumps([{"id": "hello", "version": "v1", "vars": {"name": "Ada"}, "blocks": []}]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Demo entry 'blocks' must be a mapping"):
        render_demo(str(manifest_path), str(data_path))


def test_dump_and_write_demo_results(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    data_path = tmp_path / "demo.json"
    data_path.write_text(
        json.dumps([{"id": "hello", "version": "v1", "vars": {"name": "Ada"}, "blocks": {}}]),
        encoding="utf-8",
    )

    results = render_demo(str(manifest_path), str(data_path))
    output_path = tmp_path / "out" / "demo_output.json"
    write_demo_results(results, str(output_path))

    output = output_path.read_text(encoding="utf-8")
    assert json.loads(output) == json.loads(dump_demo_results(results))
