"""Enrichment pipeline utilities."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from promptir.models import PromptDefinition

Enricher = Callable[[PromptDefinition, dict[str, str], dict[str, str]], dict[str, str]]


@dataclass
class EnrichmentPipeline:
    enrichers: list[Enricher]

    def apply(
        self,
        prompt: PromptDefinition,
        vars: dict[str, str],
        blocks: dict[str, str],
    ) -> dict[str, str]:
        """Apply enrichers sequentially, returning an updated blocks dict."""
        enriched = dict(blocks)
        for enricher in self.enrichers:
            updates = enricher(prompt, vars, dict(enriched))
            if updates:
                enriched.update(updates)
        return enriched
