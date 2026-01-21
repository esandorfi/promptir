"""promptir: local-first prompt compiler and runtime registry."""

from promptir.compiler import compile_prompts
from promptir.enrich import EnrichmentPipeline
from promptir.registry import PromptRegistry

__all__ = ["EnrichmentPipeline", "PromptRegistry", "compile_prompts"]
__version__ = "0.1.0"
