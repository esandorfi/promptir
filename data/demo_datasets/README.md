# Demo datasets

This directory contains curated prompt collections with compiled manifests and demo data
for end-to-end validation. Each dataset is self-contained: prompts live under `prompts/`,
compiled output is committed as `manifest.json`, and runnable inputs live in
`demo_data.json`.

## Available datasets

| Dataset | Purpose | Prompt root | Manifest | Demo data | Demo command |
| --- | --- | --- | --- | --- | --- |
| `document_analysis` | Document analysis workflows (single, multi, map-reduce, extraction, verification, diff) | `data/demo_datasets/document_analysis/prompts` | `data/demo_datasets/document_analysis/manifest.json` | `data/demo_datasets/document_analysis/demo_data.json` | `promptir demo-run --manifest data/demo_datasets/document_analysis/manifest.json --data data/demo_datasets/document_analysis/demo_data.json --out data/demo_datasets/document_analysis/demo_output.json` |
| `local_operations` | Local workspace interactions + documentation sections | `data/demo_datasets/local_operations/prompts` | `data/demo_datasets/local_operations/manifest.json` | `data/demo_datasets/local_operations/demo_data.json` | `promptir demo-run --manifest data/demo_datasets/local_operations/manifest.json --data data/demo_datasets/local_operations/demo_data.json --out data/demo_datasets/local_operations/demo_output.json` |

## Updating manifests (only when changed)

Run the helper script to compile every dataset and update manifests only if content
changes:

```bash
python scripts/compile_demo_datasets.py
```

This keeps `manifest.json` committed and avoids touching Git when the compiled output
is identical.

## Running demo data

The `promptir demo-run` command renders a manifest with demo data and writes a JSON
result containing the resolved prompt version, inputs, and rendered messages.

Example:

```bash
promptir demo-run \
  --manifest data/demo_datasets/document_analysis/manifest.json \
  --data data/demo_datasets/document_analysis/demo_data.json \
  --out data/demo_datasets/document_analysis/demo_output.json
```

## Model-specific guidance (Codex + Claude)

Use these datasets as a baseline when adapting to model-specific patterns:

- **Codex-style command execution**
  - Prefer explicit, stepwise instructions and code-like formatting for tool usage.
  - Keep tool inputs structured and minimal to reduce ambiguity.
- **Claude-style structured prompts**
  - Use clear sectioning (e.g. headings, bullet lists) and explicit output formats.
  - When necessary, wrap optional context in tags or labeled blocks for clarity.

These recommendations are compatible with the role-based prompt format used in
`promptir` and can be layered via prompt variants or includes.

## Future dataset ideas

- **codex_cli_playbooks**: end-to-end command-driven workflows (build, test, deploy).
- **claude_tool_chains**: multi-step reasoning prompts with tool output validation.
- **rag_eval_suite**: retrieval + citation accuracy benchmarks using controlled corpora.
