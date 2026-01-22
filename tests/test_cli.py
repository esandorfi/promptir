from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from promptir.cli import main


def _write_prompt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_cli_compile_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "hello" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "hello",
  "version": "v1",
  "metadata": {},
  "variables": []
}
---
# system
Hello.

# user
Hi.
""",
    )
    out_path = tmp_path / "dist" / "manifest.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["promptir", "compile", "--src", str(src_root), "--out", str(out_path)],
    )
    assert main() == 0
    assert out_path.exists()


def test_cli_compile_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    bad_prompt = src_root / "bad" / "v1.md"
    _write_prompt(
        bad_prompt,
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
    out_path = tmp_path / "dist" / "manifest.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["promptir", "compile", "--src", str(src_root), "--out", str(out_path)],
    )
    assert main() == 1


def test_cli_demo_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "hello" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "hello",
  "version": "v1",
  "metadata": {},
  "variables": ["name"]
}
---
# system
Hello {{name}}.

# user
Hi {{name}}.
""",
    )
    manifest_path = tmp_path / "dist" / "manifest.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["promptir", "compile", "--src", str(src_root), "--out", str(manifest_path)],
    )
    assert main() == 0

    demo_data = [
        {"id": "hello", "version": "v1", "vars": {"name": "Ada"}, "blocks": {}},
    ]
    demo_data_path = tmp_path / "demo.json"
    demo_data_path.write_text(json.dumps(demo_data), encoding="utf-8")

    output_path = tmp_path / "output.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "promptir",
            "demo-run",
            "--manifest",
            str(manifest_path),
            "--data",
            str(demo_data_path),
            "--out",
            str(output_path),
        ],
    )
    assert main() == 0
    assert output_path.exists()


def test_cli_demo_run_stdout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "hello" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "hello",
  "version": "v1",
  "metadata": {},
  "variables": ["name"]
}
---
# system
Hello {{name}}.

# user
Hi {{name}}.
""",
    )
    manifest_path = tmp_path / "dist" / "manifest.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["promptir", "compile", "--src", str(src_root), "--out", str(manifest_path)],
    )
    assert main() == 0

    demo_data = [
        {"id": "hello", "version": "v1", "vars": {"name": "Ada"}, "blocks": {}},
    ]
    demo_data_path = tmp_path / "demo.json"
    demo_data_path.write_text(json.dumps(demo_data), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "promptir",
            "demo-run",
            "--manifest",
            str(manifest_path),
            "--data",
            str(demo_data_path),
        ],
    )
    assert main() == 0
    assert "Hello Ada." in capsys.readouterr().out


def test_cli_demo_run_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "hello" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "hello",
  "version": "v1",
  "metadata": {},
  "variables": ["name"]
}
---
# system
Hello {{name}}.

# user
Hi {{name}}.
""",
    )
    manifest_path = tmp_path / "dist" / "manifest.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["promptir", "compile", "--src", str(src_root), "--out", str(manifest_path)],
    )
    assert main() == 0

    demo_data_path = tmp_path / "demo.json"
    demo_data_path.write_text(json.dumps({"id": "hello"}), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "promptir",
            "demo-run",
            "--manifest",
            str(manifest_path),
            "--data",
            str(demo_data_path),
        ],
    )
    assert main() == 1


def test_cli_no_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["promptir"])
    assert main() == 1


def test_cli_module_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["promptir"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("promptir.cli", run_name="__main__")
    assert excinfo.value.code == 1
