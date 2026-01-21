"""Simple template renderer with {{var}} substitution."""

from __future__ import annotations

import re
from collections.abc import Mapping

_TOKEN_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


def render_simple(template: str, values: Mapping[str, str]) -> str:
    """Render simple templates by replacing {{var}} tokens."""

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return values.get(key, "")

    return _TOKEN_PATTERN.sub(replace, template)
