"""Core dataclasses used across compiler and runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BlockSpec:
    optional: bool = True
    default: str | None = ""


@dataclass(frozen=True)
class PromptMessage:
    role: str
    content: str


@dataclass(frozen=True)
class PromptDefinition:
    id: str
    version: str
    metadata: dict[str, Any]
    template_engine: str
    variables: tuple[str, ...]
    blocks: dict[str, BlockSpec]
    messages: tuple[PromptMessage, ...]
    hash: str

    @property
    def block_names(self) -> set[str]:
        return set(self.blocks.keys())

    @property
    def required_vars(self) -> set[str]:
        return set(self.variables) - self.block_names
