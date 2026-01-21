"""Prompt registry for runtime rendering."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from promptir.enrich import EnrichmentPipeline
from promptir.errors import PromptInputError, PromptNotFound
from promptir.models import BlockSpec, PromptDefinition, PromptMessage
from promptir.render_jinja2 import render_jinja2
from promptir.render_simple import render_simple


@dataclass(frozen=True)
class RenderedPrompt:
    messages: tuple[dict[str, str], ...]


class PromptRegistry:
    def __init__(
        self,
        prompts: dict[tuple[str, str], PromptDefinition],
        *,
        strict_inputs: bool = True,
    ) -> None:
        self._prompts = prompts
        self._strict_inputs = strict_inputs
        self._latest_versions = _calculate_latest_versions(prompts)
        self._pipeline: EnrichmentPipeline | None = None

    @classmethod
    def from_manifest_path(cls, path: str, *, strict_inputs: bool = True) -> PromptRegistry:
        manifest_path = Path(path)
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        prompts = _load_prompts(data)
        return cls(prompts, strict_inputs=strict_inputs)

    def set_enrichment_pipeline(self, pipeline: EnrichmentPipeline) -> None:
        self._pipeline = pipeline

    def render(
        self,
        prompt_id: str,
        *,
        version: str | None = None,
        vars: dict[str, Any] | None = None,
        blocks: dict[str, Any] | None = None,
    ) -> RenderedPrompt:
        prompt = self._get_prompt(prompt_id, version)
        vars = vars or {}
        blocks = blocks or {}
        normalized_vars = _normalize_values(vars)
        normalized_blocks = _normalize_values(blocks)

        if self._strict_inputs:
            _validate_inputs(prompt, normalized_vars, normalized_blocks)

        blocks_with_defaults = _apply_block_defaults(prompt, normalized_blocks)

        if self._pipeline is not None:
            enriched_blocks = self._pipeline.apply(prompt, normalized_vars, blocks_with_defaults)
            if self._strict_inputs:
                _validate_enriched_blocks(prompt, enriched_blocks)
        else:
            enriched_blocks = blocks_with_defaults

        values = {**normalized_vars, **enriched_blocks}
        rendered_messages = tuple(
            {"role": message.role, "content": _render_message(prompt, message, values)}
            for message in prompt.messages
        )
        return RenderedPrompt(messages=rendered_messages)

    def _get_prompt(self, prompt_id: str, version: str | None) -> PromptDefinition:
        resolved_version = version or self._latest_versions.get(prompt_id)
        if resolved_version is None:
            raise PromptNotFound(f"Prompt id not found: {prompt_id}")
        key = (prompt_id, resolved_version)
        prompt = self._prompts.get(key)
        if prompt is None:
            raise PromptNotFound(f"Prompt not found: {prompt_id}@{resolved_version}")
        return prompt


def _load_prompts(manifest: dict[str, Any]) -> dict[tuple[str, str], PromptDefinition]:
    prompts: dict[tuple[str, str], PromptDefinition] = {}
    for entry in manifest.get("prompts", []):
        blocks = {
            name: BlockSpec(optional=spec["optional"], default=spec["default"])
            for name, spec in entry.get("blocks", {}).items()
        }
        messages = tuple(
            PromptMessage(role=msg["role"], content=msg["content"])
            for msg in entry.get("messages", [])
        )
        prompt = PromptDefinition(
            id=entry["id"],
            version=entry["version"],
            metadata=entry["metadata"],
            template_engine=entry["template_engine"],
            variables=tuple(entry["variables"]),
            blocks=blocks,
            messages=messages,
            hash=entry["hash"],
        )
        prompts[(prompt.id, prompt.version)] = prompt
    return prompts


def _calculate_latest_versions(prompts: dict[tuple[str, str], PromptDefinition]) -> dict[str, str]:
    latest: dict[str, str] = {}
    for prompt_id, version in prompts:
        current = latest.get(prompt_id)
        if current is None or version > current:
            latest[prompt_id] = version
    return latest


def _normalize_values(values: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in values.items():
        if value is None:
            normalized[key] = ""
        elif isinstance(value, str):
            normalized[key] = value
        else:
            normalized[key] = str(value)
    return normalized


def _validate_inputs(
    prompt: PromptDefinition, vars: dict[str, str], blocks: dict[str, str]
) -> None:
    missing_vars = prompt.required_vars - set(vars.keys())
    if missing_vars:
        raise PromptInputError(f"Missing required vars: {sorted(missing_vars)}")
    extra_vars = set(vars.keys()) - prompt.required_vars
    if extra_vars:
        raise PromptInputError(f"Extra vars provided: {sorted(extra_vars)}")
    extra_blocks = set(blocks.keys()) - prompt.block_names
    if extra_blocks:
        raise PromptInputError(f"Extra blocks provided: {sorted(extra_blocks)}")


def _apply_block_defaults(prompt: PromptDefinition, blocks: dict[str, str]) -> dict[str, str]:
    merged = dict(blocks)
    for name, spec in prompt.blocks.items():
        if name in merged:
            continue
        if spec.optional:
            merged[name] = spec.default if spec.default is not None else ""
        else:
            raise PromptInputError(f"Missing required block: {name}")
    return merged


def _validate_enriched_blocks(prompt: PromptDefinition, blocks: dict[str, str]) -> None:
    extra = set(blocks.keys()) - prompt.block_names
    if extra:
        raise PromptInputError(f"Enrichers introduced undeclared blocks: {sorted(extra)}")


def _render_message(
    prompt: PromptDefinition, message: PromptMessage, values: dict[str, str]
) -> str:
    if prompt.template_engine == "simple":
        return render_simple(message.content, values)
    if prompt.template_engine == "jinja2_sandbox":
        return render_jinja2(message.content, values)
    raise PromptInputError(
        f"Unknown template_engine '{prompt.template_engine}' for {prompt.id}@{prompt.version}"
    )
