# Agent Instructions

## Build Instructions
- Use `promptir compile --src src/llm/prompts --out dist/llm_prompts/manifest.json` to compile prompt sources.
- Ensure prompt sources follow the path/id/version rules defined in build_specifications.md.

## Check Instructions
- Run `python -m ruff check .` for linting.
- Run `python -m ruff format --check .` for formatting.
- Run `python -m pyright` for type checking.
- Run `python -m pytest` for tests (coverage is required).

## Rules
- Keep variables and blocks strictly separated; underscore-prefixed names are blocks only.
- Every declared variable/block must be referenced at least once in prompt content.
- Avoid introducing undeclared blocks during enrichment in strict mode.
- Maintain 100% test coverage for the promptir package.
