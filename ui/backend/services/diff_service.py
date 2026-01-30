"""Diff computation for prompt versions."""

import difflib
import json
from .prompt_service import load_prompt_source, parse_prompt_content


def compute_diff(
    prompts_dir: str,
    prompt_id: str,
    version1: str,
    version2: str,
) -> tuple[str, str] | None:
    """Compute diff between two versions of a prompt.

    Returns tuple of (frontmatter_diff, template_diff) or None if sources not found.
    """
    source1 = load_prompt_source(prompts_dir, prompt_id, version1)
    source2 = load_prompt_source(prompts_dir, prompt_id, version2)

    if not source1 or not source2:
        return None

    fm1, body1 = parse_prompt_content(source1.content)
    fm2, body2 = parse_prompt_content(source2.content)

    # Compute frontmatter diff
    fm1_str = json.dumps(fm1, indent=2, sort_keys=True) if fm1 else ""
    fm2_str = json.dumps(fm2, indent=2, sort_keys=True) if fm2 else ""

    frontmatter_diff = "\n".join(
        difflib.unified_diff(
            fm1_str.splitlines(),
            fm2_str.splitlines(),
            fromfile=f"{prompt_id}@{version1} (frontmatter)",
            tofile=f"{prompt_id}@{version2} (frontmatter)",
            lineterm="",
        )
    )

    # Compute template diff
    template_diff = "\n".join(
        difflib.unified_diff(
            body1.splitlines(),
            body2.splitlines(),
            fromfile=f"{prompt_id}@{version1} (template)",
            tofile=f"{prompt_id}@{version2} (template)",
            lineterm="",
        )
    )

    return frontmatter_diff, template_diff
