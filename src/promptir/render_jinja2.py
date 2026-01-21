"""Sandboxed Jinja2 renderer."""

from __future__ import annotations

from collections.abc import Mapping

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment


def render_jinja2(template: str, values: Mapping[str, str]) -> str:
    """Render a template using a locked-down sandbox environment."""
    env = SandboxedEnvironment(
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals = {}
    env.filters = {}
    env.tests = {}
    return env.from_string(template).render(**values)
