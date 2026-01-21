from __future__ import annotations

from pathlib import Path

import pytest

from promptir.compiler import compile_prompts
from promptir.enrich import EnrichmentPipeline
from promptir.errors import PromptInputError, PromptNotFound
from promptir.registry import PromptRegistry


def _write_prompt(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _compile_sample(tmp_path: Path) -> Path:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "planner" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "planner",
  "version": "v1",
  "metadata": {},
  "variables": ["question"],
  "blocks": {
    "_context": {"optional": false, "default": ""}
  }
}
---
# system
System.

# user
Q: {{question}}
Context: {{_context}}
""",
    )
    out_path = tmp_path / "dist" / "manifest.json"
    compile_prompts(str(src_root), str(out_path))
    return out_path


def _compile_optional_block_sample(tmp_path: Path) -> Path:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "optional" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "optional",
  "version": "v1",
  "metadata": {},
  "variables": ["question"],
  "blocks": {
    "_context": {"optional": true, "default": "default"}
  }
}
---
# system
System.

# user
Q: {{question}}
Context: {{_context}}
""",
    )
    out_path = tmp_path / "dist" / "manifest.json"
    compile_prompts(str(src_root), str(out_path))
    return out_path


def test_registry_render_and_defaults(tmp_path: Path) -> None:
    manifest_path = _compile_sample(tmp_path)
    registry = PromptRegistry.from_manifest_path(str(manifest_path))
    rendered = registry.render(
        "planner",
        version="v1",
        vars={"question": "Hello"},
        blocks={"_context": "CTX"},
    )
    assert rendered.messages[1]["content"].startswith("Q: Hello")


def test_registry_normalizes_none(tmp_path: Path) -> None:
    manifest_path = _compile_sample(tmp_path)
    registry = PromptRegistry.from_manifest_path(str(manifest_path))
    rendered = registry.render(
        "planner",
        version="v1",
        vars={"question": "Hello"},
        blocks={"_context": None},
    )
    assert "Context: " in rendered.messages[1]["content"]


def test_registry_missing_prompt(tmp_path: Path) -> None:
    manifest_path = _compile_sample(tmp_path)
    registry = PromptRegistry.from_manifest_path(str(manifest_path))
    with pytest.raises(PromptNotFound):
        registry.render("unknown", vars={}, blocks={})


def test_registry_strict_inputs(tmp_path: Path) -> None:
    manifest_path = _compile_sample(tmp_path)
    registry = PromptRegistry.from_manifest_path(str(manifest_path))
    with pytest.raises(PromptInputError, match="Missing required vars"):
        registry.render("planner", version="v1", vars={}, blocks={"_context": ""})
    with pytest.raises(PromptInputError, match="Extra vars"):
        registry.render(
            "planner",
            version="v1",
            vars={"question": "Hi", "extra": "no"},
            blocks={"_context": ""},
        )
    with pytest.raises(PromptInputError, match="Extra blocks"):
        registry.render(
            "planner",
            version="v1",
            vars={"question": "Hi"},
            blocks={"_context": "", "_extra": "bad"},
        )
    with pytest.raises(PromptInputError, match="Missing required block"):
        registry.render("planner", version="v1", vars={"question": "Hi"}, blocks={})


def test_registry_missing_version(tmp_path: Path) -> None:
    manifest_path = _compile_sample(tmp_path)
    registry = PromptRegistry.from_manifest_path(str(manifest_path))
    with pytest.raises(PromptNotFound, match="Prompt not found"):
        registry.render("planner", version="v2", vars={"question": "Hi"}, blocks={"_context": ""})


def test_registry_optional_defaults_and_normalization(tmp_path: Path) -> None:
    manifest_path = _compile_optional_block_sample(tmp_path)
    registry = PromptRegistry.from_manifest_path(str(manifest_path))
    rendered = registry.render("optional", vars={"question": 42}, blocks={})
    assert "Q: 42" in rendered.messages[1]["content"]
    assert "default" in rendered.messages[1]["content"]


def test_registry_enrichment_pipeline(tmp_path: Path) -> None:
    manifest_path = _compile_sample(tmp_path)
    registry = PromptRegistry.from_manifest_path(str(manifest_path))

    def enricher(prompt: object, vars: dict[str, str], blocks: dict[str, str]) -> dict[str, str]:
        return {"_context": f"enriched:{vars['question']}"}

    registry.set_enrichment_pipeline(EnrichmentPipeline([enricher]))
    rendered = registry.render(
        "planner", version="v1", vars={"question": "Hi"}, blocks={"_context": ""}
    )
    assert "enriched:Hi" in rendered.messages[1]["content"]


def test_registry_enrichment_strict_block_check(tmp_path: Path) -> None:
    manifest_path = _compile_sample(tmp_path)
    registry = PromptRegistry.from_manifest_path(str(manifest_path))

    def bad_enricher(
        prompt: object, vars: dict[str, str], blocks: dict[str, str]
    ) -> dict[str, str]:
        return {"_new_block": "oops"}

    registry.set_enrichment_pipeline(EnrichmentPipeline([bad_enricher]))
    with pytest.raises(PromptInputError, match="Enrichers introduced"):
        registry.render("planner", version="v1", vars={"question": "Hi"}, blocks={"_context": ""})


def test_registry_jinja2_render(tmp_path: Path) -> None:
    src_root = tmp_path / "src" / "llm" / "prompts"
    prompt_path = src_root / "router" / "v1.md"
    _write_prompt(
        prompt_path,
        """---
{
  "id": "router",
  "version": "v1",
  "template_engine": "jinja2_sandbox",
  "metadata": {},
  "variables": ["question"],
  "blocks": {
    "_context": {"optional": true, "default": ""}
  }
}
---
# system
System.

# user
Question: {{ question }}
{% if _context %}Context: {{ _context }}{% endif %}
""",
    )
    out_path = tmp_path / "dist" / "manifest.json"
    compile_prompts(str(src_root), str(out_path))
    registry = PromptRegistry.from_manifest_path(str(out_path))
    rendered = registry.render(
        "router",
        version="v1",
        vars={"question": "Hi"},
        blocks={"_context": "CTX"},
    )
    assert "CTX" in rendered.messages[1]["content"]


def test_registry_unknown_template_engine(tmp_path: Path) -> None:
    manifest_path = tmp_path / "dist" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        """
{
  "schema_version": 1,
  "prompts": [
    {
      "id": "bad",
      "version": "v1",
      "metadata": {},
      "template_engine": "unknown",
      "variables": ["question"],
      "blocks": {},
      "messages": [
        {"role": "system", "content": "Hi"},
        {"role": "user", "content": "{{question}}"}
      ],
      "hash": "abc"
    }
  ]
}
""",
        encoding="utf-8",
    )
    registry = PromptRegistry.from_manifest_path(str(manifest_path))
    with pytest.raises(PromptInputError, match="Unknown template_engine"):
        registry.render("bad", version="v1", vars={"question": "hi"}, blocks={})
