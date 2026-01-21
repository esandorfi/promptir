"""Helper script to compile prompts."""

from promptir.compiler import compile_prompts

if __name__ == "__main__":
    compile_prompts("src/llm/prompts", "dist/llm_prompts/manifest.json")
