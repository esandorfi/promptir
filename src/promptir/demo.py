"""Run prompt manifests against demo datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from promptir.registry import PromptRegistry


def render_demo(manifest_path: str, data_path: str) -> list[dict[str, Any]]:
    registry = PromptRegistry.from_manifest_path(manifest_path)
    entries = _load_demo_data(data_path)
    results: list[dict[str, Any]] = []
    for entry in entries:
        prompt_id = _require_str(entry, "id")
        version = entry.get("version")
        if version is not None and not isinstance(version, str):
            raise ValueError("Demo entry 'version' must be a string when provided.")
        vars_payload = _require_dict(entry, "vars")
        blocks_payload = _require_dict(entry, "blocks")
        prompt = registry._get_prompt(prompt_id, version)
        rendered = registry.render(
            prompt_id,
            version=version,
            vars=vars_payload,
            blocks=blocks_payload,
        )
        results.append(
            {
                "id": prompt.id,
                "version": prompt.version,
                "vars": vars_payload,
                "blocks": blocks_payload,
                "messages": list(rendered.messages),
            }
        )
    return results


def dump_demo_results(results: list[dict[str, Any]]) -> str:
    return json.dumps(results, indent=2, sort_keys=True)


def write_demo_results(results: list[dict[str, Any]], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_demo_results(results), encoding="utf-8")


def _load_demo_data(data_path: str) -> list[dict[str, Any]]:
    path = Path(data_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Demo data must be a list of prompt entries.")
    return data


def _require_str(entry: dict[str, Any], key: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str):
        raise ValueError(f"Demo entry '{key}' must be a string.")
    return value


def _require_dict(entry: dict[str, Any], key: str) -> dict[str, Any]:
    value = entry.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Demo entry '{key}' must be a mapping when provided.")
    return value
