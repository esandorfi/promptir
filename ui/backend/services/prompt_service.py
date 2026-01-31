"""Prompt file and manifest operations."""

import json
from pathlib import Path

from ..schemas import BlockSpec, PromptSource, PromptSummary


def load_manifest(manifest_path: str) -> dict | None:
    """Load a compiled manifest file."""
    path = Path(manifest_path)
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def load_prompt_source(prompts_dir: str, prompt_id: str, version: str) -> PromptSource | None:
    """Load raw source file for a prompt."""
    prompts_path = Path(prompts_dir)

    # Check regular prompt path
    prompt_path = prompts_path / prompt_id / f"{version}.md"

    # Also check _includes path for includes
    if not prompt_path.exists():
        prompt_path = prompts_path / "_includes" / prompt_id / f"{version}.md"

    if not prompt_path.exists():
        return None

    with open(prompt_path) as f:
        content = f.read()

    return PromptSource(
        id=prompt_id,
        version=version,
        content=content,
        path=str(prompt_path),
    )


def save_prompt_source(
    prompts_dir: str, prompt_id: str, version: str, content: str
) -> PromptSource | None:
    """Save a prompt source file."""
    prompts_path = Path(prompts_dir)

    # Determine if this is an include (starts with _)
    if prompt_id.startswith("_"):
        # This is probably meant for _includes - remove underscore prefix
        actual_id = prompt_id[1:] if prompt_id.startswith("_") else prompt_id
        prompt_dir = prompts_path / "_includes" / actual_id
    else:
        prompt_dir = prompts_path / prompt_id

    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / f"{version}.md"

    with open(prompt_path, "w") as f:
        f.write(content)

    return PromptSource(
        id=prompt_id,
        version=version,
        content=content,
        path=str(prompt_path),
    )


def list_prompt_files(prompts_dir: str) -> list[PromptSummary]:
    """List prompts by scanning the directory (fallback when no manifest)."""
    prompts_path = Path(prompts_dir)
    if not prompts_path.exists():
        return []

    prompts = []
    for prompt_dir in prompts_path.iterdir():
        if prompt_dir.is_dir() and not prompt_dir.name.startswith("_"):
            for version_file in prompt_dir.glob("*.md"):
                version = version_file.stem
                content = version_file.read_text()
                frontmatter = _parse_frontmatter(content)

                if frontmatter:
                    prompts.append(
                        PromptSummary(
                            id=prompt_dir.name,
                            version=version,
                            template_engine=frontmatter.get("template_engine", "simple"),
                            metadata=frontmatter.get("metadata", {}),
                            variables=[
                                v for v in frontmatter.get("variables", []) if not v.startswith("_")
                            ],
                            blocks={
                                k: BlockSpec(**v) for k, v in frontmatter.get("blocks", {}).items()
                            },
                        )
                    )

    return prompts


def get_includes(prompts_dir: str) -> list[PromptSummary]:
    """List include files."""
    includes_path = Path(prompts_dir) / "_includes"
    if not includes_path.exists():
        return []

    includes = []
    for include_dir in includes_path.iterdir():
        if include_dir.is_dir():
            for version_file in include_dir.glob("*.md"):
                version = version_file.stem
                content = version_file.read_text()
                frontmatter = _parse_frontmatter(content)

                includes.append(
                    PromptSummary(
                        id=include_dir.name,
                        version=version,
                        template_engine=frontmatter.get("template_engine", "simple")
                        if frontmatter
                        else "simple",
                        metadata=frontmatter.get("metadata", {}) if frontmatter else {},
                        variables=[],
                        blocks={},
                    )
                )

    return includes


def _parse_frontmatter(content: str) -> dict | None:
    """Parse JSON frontmatter from prompt content."""
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return None

    # Find closing ---
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None

    frontmatter_lines = lines[1:end_idx]
    frontmatter_str = "\n".join(frontmatter_lines)

    try:
        return json.loads(frontmatter_str)
    except json.JSONDecodeError:
        return None


def parse_prompt_content(content: str) -> tuple[dict | None, str]:
    """Parse prompt into frontmatter dict and body."""
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return None, content

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, content

    frontmatter_lines = lines[1:end_idx]
    frontmatter_str = "\n".join(frontmatter_lines)
    body = "\n".join(lines[end_idx + 1 :])

    try:
        frontmatter = json.loads(frontmatter_str)
        return frontmatter, body
    except json.JSONDecodeError:
        return None, content
