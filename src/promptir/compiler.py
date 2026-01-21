"""Prompt compiler that validates and builds a manifest."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

from jinja2 import Environment, meta

from promptir.errors import PromptCompileError
from promptir.models import BlockSpec, PromptMessage

_VARIABLE_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")
_VARIABLE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_BLOCK_NAME_PATTERN = re.compile(r"^_[a-z][a-z0-9_]*$")
_ALLOWED_ENGINES = {"simple", "jinja2_sandbox"}


class PromptDocument:
    def __init__(self, frontmatter: dict[str, Any], sections: dict[str, str]) -> None:
        self.frontmatter = frontmatter
        self.sections = sections


def compile_prompts(src_root: str, out_path: str) -> dict[str, Any]:
    """Compile prompts from src_root into a manifest written to out_path."""
    src_path = Path(src_root)
    if not src_path.exists():
        raise PromptCompileError(f"Source root not found: {src_root}")

    prompt_files = _collect_prompt_files(src_path)
    prompts: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for prompt_file in prompt_files:
        prompt_doc = _load_prompt_document(prompt_file, src_path, is_include=False)
        frontmatter = prompt_doc.frontmatter
        includes = frontmatter.get("includes", [])
        merged_sections = dict(prompt_doc.sections)
        for include_ref in includes:
            include_doc = _load_include_document(src_path, include_ref)
            for role, content in include_doc.sections.items():
                existing = merged_sections.get(role, "")
                merged_sections[role] = _merge_role_content(content, existing)

        _ensure_required_roles(prompt_file, merged_sections)
        variables = _validate_variables(frontmatter, prompt_file)
        blocks = _validate_blocks(frontmatter, prompt_file)
        template_engine = frontmatter.get("template_engine", "simple")
        _validate_template_engine(template_engine, prompt_file)

        _validate_declared_names(variables, blocks, prompt_file)
        used_names = _extract_used_names(template_engine, merged_sections)
        _validate_used_names(used_names, variables, blocks, prompt_file)

        prompt_id = frontmatter["id"]
        version = frontmatter["version"]
        if (prompt_id, version) in seen:
            raise PromptCompileError(
                f"Duplicate prompt id/version: {prompt_id}@{version} in {prompt_file}"
            )
        seen.add((prompt_id, version))

        prompt_entry = _build_prompt_entry(
            frontmatter,
            variables,
            blocks,
            template_engine,
            merged_sections,
        )
        prompts.append(prompt_entry)

    manifest = {"schema_version": 1, "prompts": prompts}
    _write_manifest(out_path, manifest)
    return manifest


def _collect_prompt_files(src_path: Path) -> list[Path]:
    prompt_files: list[Path] = []
    for root, dirs, files in os.walk(src_path):
        if "_includes" in dirs:
            dirs.remove("_includes")
        for filename in files:
            if filename.endswith(".md"):
                prompt_files.append(Path(root) / filename)
    return sorted(prompt_files)


def _load_include_document(src_path: Path, include_ref: str) -> PromptDocument:
    if "@" not in include_ref:
        raise PromptCompileError(f"Invalid include reference: {include_ref}")
    name, version = include_ref.split("@", 1)
    include_path = src_path / "_includes" / name / f"{version}.md"
    if not include_path.exists():
        raise PromptCompileError(f"Missing include file: {include_path}")
    return _load_prompt_document(include_path, src_path, is_include=True)


def _load_prompt_document(path: Path, src_path: Path, is_include: bool) -> PromptDocument:
    frontmatter, body = _parse_frontmatter(path)
    _validate_frontmatter(frontmatter, path)
    _validate_path_consistency(frontmatter, path, src_path, is_include=is_include)
    sections = _parse_sections(body, path)
    return PromptDocument(frontmatter, sections)


def _parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise PromptCompileError(f"Missing frontmatter delimiter in {path}")
    try:
        end_index = lines.index("---", 1)
    except ValueError as exc:
        raise PromptCompileError(f"Missing closing frontmatter delimiter in {path}") from exc
    json_block = "\n".join(lines[1:end_index]).strip()
    if not json_block:
        raise PromptCompileError(f"Empty frontmatter in {path}")
    try:
        frontmatter = json.loads(json_block)
    except json.JSONDecodeError as exc:
        raise PromptCompileError(f"Invalid JSON frontmatter in {path}: {exc}") from exc
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return frontmatter, body


def _parse_sections(body: str, path: Path) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_role: str | None = None
    for line in body.splitlines():
        if line.startswith("# "):
            role = line[2:].strip().lower()
            if role not in {"system", "user", "assistant"}:
                raise PromptCompileError(f"Invalid role heading '{line}' in {path}")
            current_role = role
            sections.setdefault(role, [])
            continue
        if line.startswith("#"):
            raise PromptCompileError(
                f"Invalid heading '{line}' in {path}; only single-level role headings allowed"
            )
        if current_role is None:
            if line.strip():
                raise PromptCompileError(f"Content before first role heading in {path}")
            continue
        sections[current_role].append(line)
    return {role: "\n".join(lines).strip() for role, lines in sections.items()}


def _ensure_required_roles(path: Path, sections: dict[str, str]) -> None:
    missing = {"system", "user"} - set(sections.keys())
    if missing:
        raise PromptCompileError(f"Missing required roles {sorted(missing)} in {path}")


def _validate_frontmatter(frontmatter: dict[str, Any], path: Path) -> None:
    required_fields = ["id", "version", "metadata", "variables"]
    for field in required_fields:
        if field not in frontmatter:
            raise PromptCompileError(f"Missing frontmatter field '{field}' in {path}")
    if not isinstance(frontmatter["id"], str) or not frontmatter["id"]:
        raise PromptCompileError(f"Invalid id in {path}")
    if not isinstance(frontmatter["version"], str) or not frontmatter["version"]:
        raise PromptCompileError(f"Invalid version in {path}")
    if not isinstance(frontmatter["metadata"], dict):
        raise PromptCompileError(f"Invalid metadata in {path}")
    if not isinstance(frontmatter["variables"], list):
        raise PromptCompileError(f"Invalid variables in {path}")


def _validate_path_consistency(
    frontmatter: dict[str, Any],
    path: Path,
    src_path: Path,
    *,
    is_include: bool,
) -> None:
    rel_path = path.relative_to(src_path)
    parts = rel_path.parts
    if is_include:
        if len(parts) != 3 or parts[0] != "_includes":
            raise PromptCompileError(f"Invalid include path: {rel_path}")
        _, include_name, version_file = parts
        version = version_file.removesuffix(".md")
        if frontmatter["id"] != include_name or frontmatter["version"] != version:
            raise PromptCompileError(f"Include id/version mismatch in {path}")
        return
    if len(parts) != 2:
        raise PromptCompileError(f"Invalid prompt path (expected <id>/<version>.md): {rel_path}")
    prompt_id, version_file = parts
    version = version_file.removesuffix(".md")
    if frontmatter["id"] != prompt_id or frontmatter["version"] != version:
        raise PromptCompileError(f"Prompt id/version mismatch in {path}")


def _validate_variables(frontmatter: dict[str, Any], path: Path) -> list[str]:
    variables = frontmatter.get("variables", [])
    if not isinstance(variables, list):
        raise PromptCompileError(f"Invalid variables in {path}")
    for name in variables:
        if not isinstance(name, str) or not _VARIABLE_NAME_PATTERN.match(name):
            raise PromptCompileError(f"Invalid variable name '{name}' in {path}")
    return variables


def _validate_blocks(frontmatter: dict[str, Any], path: Path) -> dict[str, BlockSpec]:
    blocks_raw = frontmatter.get("blocks", {})
    if blocks_raw is None:
        return {}
    if not isinstance(blocks_raw, dict):
        raise PromptCompileError(f"Invalid blocks in {path}")
    typed_blocks_raw: dict[object, Any] = blocks_raw
    blocks: dict[str, BlockSpec] = {}
    for name, spec in typed_blocks_raw.items():
        if not isinstance(name, str) or not _BLOCK_NAME_PATTERN.match(name):
            raise PromptCompileError(f"Invalid block name '{name}' in {path}")
        if not isinstance(spec, dict):
            raise PromptCompileError(f"Invalid block spec for '{name}' in {path}")
        typed_spec: dict[str, Any] = spec
        optional = typed_spec.get("optional", True)
        default = typed_spec.get("default", "")
        if not isinstance(optional, bool):
            raise PromptCompileError(f"Invalid optional flag for '{name}' in {path}")
        if default is not None and not isinstance(default, str):
            raise PromptCompileError(f"Invalid default for '{name}' in {path}")
        blocks[name] = BlockSpec(optional=optional, default=default)
    return blocks


def _validate_template_engine(template_engine: str, path: Path) -> None:
    if template_engine not in _ALLOWED_ENGINES:
        raise PromptCompileError(f"Invalid template_engine '{template_engine}' in {path}")


def _validate_declared_names(
    variables: list[str],
    blocks: dict[str, BlockSpec],
    path: Path,
) -> None:
    overlap = set(variables) & set(blocks.keys())
    if overlap:
        raise PromptCompileError(f"Variables and blocks overlap in {path}: {sorted(overlap)}")


def _extract_used_names(template_engine: str, sections: dict[str, str]) -> set[str]:
    merged_text = "\n".join(sections.values())
    if template_engine == "simple":
        return set(_VARIABLE_PATTERN.findall(merged_text))
    env = Environment()
    ast = cast(Any, env.parse(merged_text))
    undeclared = cast(Iterable[str], meta.find_undeclared_variables(ast))
    return set(undeclared)


def _validate_used_names(
    used_names: set[str],
    variables: list[str],
    blocks: dict[str, BlockSpec],
    path: Path,
) -> None:
    declared = set(variables) | set(blocks.keys())
    undeclared = used_names - declared
    if undeclared:
        raise PromptCompileError(f"Undeclared names in {path}: {sorted(undeclared)}")
    unused = declared - used_names
    if unused:
        raise PromptCompileError(f"Declared but unused names in {path}: {sorted(unused)}")
    invalid_block_refs = {name for name in used_names if name.startswith("_")}
    invalid_block_refs -= set(blocks.keys())
    if invalid_block_refs:
        raise PromptCompileError(
            f"Underscore names must be blocks in {path}: {sorted(invalid_block_refs)}"
        )


def _merge_role_content(include_content: str, existing: str) -> str:
    if existing:
        return f"{include_content}\n\n{existing}".strip()
    return include_content.strip()


def _build_prompt_entry(
    frontmatter: dict[str, Any],
    variables: list[str],
    blocks: dict[str, BlockSpec],
    template_engine: str,
    sections: dict[str, str],
) -> dict[str, Any]:
    messages = _build_messages(sections)
    manifest_vars = sorted(set(variables) | set(blocks.keys()))
    prompt_data = {
        "id": frontmatter["id"],
        "version": frontmatter["version"],
        "metadata": frontmatter["metadata"],
        "template_engine": template_engine,
        "variables": manifest_vars,
        "blocks": {name: asdict(spec) for name, spec in blocks.items()},
        "messages": [asdict(message) for message in messages],
    }
    prompt_hash = _hash_prompt(prompt_data)
    prompt_data["hash"] = prompt_hash
    return prompt_data


def _build_messages(sections: dict[str, str]) -> tuple[PromptMessage, ...]:
    messages = [
        PromptMessage(role="system", content=sections["system"]),
        PromptMessage(role="user", content=sections["user"]),
    ]
    if "assistant" in sections:
        messages.append(PromptMessage(role="assistant", content=sections["assistant"]))
    return tuple(messages)


def _hash_prompt(prompt_data: dict[str, Any]) -> str:
    canonical_json = json.dumps(prompt_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def _write_manifest(out_path: str, manifest: dict[str, Any]) -> None:
    output_path = Path(out_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
