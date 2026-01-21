Below is a complete, implementation-ready specification you can hand to an engineer/agent to build from scratch. It includes everything we discussed: Markdown+JSON frontmatter, versioned paths, includes, variables vs blocks separation (underscore convention), compiler to manifest, runtime registry, enrichment pipeline, strict validation, and optional Jinja2 sandbox support.

---

# Local Prompt Management Spec (Python Runtime)

## Goals

* Prompts are **authored as versioned Markdown files** in Git.
* Prompts compile to a **single manifest artifact** for fast runtime loading.
* Runtime supports:

  * **Strict input validation** (no missing required vars, no extras)
  * **Enrichment-ready “blocks”** with defaults
  * **Includes/partials** (reusable prompt fragments)
  * **Two template engines**:

    * `simple` (safe `{{var}}` substitution)
    * `jinja2_sandbox` (opt-in, sandboxed, strict undefined)
* No cloud dependency.

## Non-goals

* No UI, no hosted service.
* No evaluation framework requirement.
* No live prompt editing at runtime (manifest is the prod artifact; optional dev mode is allowed but not required).

---

# 1) Repository Layout

## Source prompts

```
src/llm/prompts/
  <id>/
    <version>.md
  _includes/
    <name>/
      <version>.md
```

### Examples

* `src/llm/prompts/planner/v1.md`
* `src/llm/prompts/_includes/policy/v3.md`

## Build output

```
dist/llm_prompts/
  manifest.json
```

## Python package (suggested)

```
llm_prompts/
  __init__.py
  models.py
  compiler.py
  registry.py
  render_simple.py
  render_jinja2.py
  enrich.py
scripts/
  compile_prompts.py
```

---

# 2) Prompt File Format

Each prompt file is Markdown containing:

1. A JSON frontmatter block delimited by `---`
2. A Markdown body split into role sections by headings

## 2.1 Frontmatter JSON (Prompt)

### Required fields

* `id: string`
* `version: string`
* `metadata: object` (can be empty `{}`)
* `variables: string[]` (required vars; can be empty)

### Optional fields

* `includes: string[]` — list of include references `"<name>@<version>"`
* `blocks: object` — mapping blockName → blockSpec
* `template_engine: "simple" | "jinja2_sandbox"` — default `"simple"`

### BlockSpec schema

* `optional: boolean` (default `true`)
* `default: string | null` (default `""`)

### Naming convention (mandatory)

* Variables (`variables[]`) must match: `^[a-z][a-z0-9_]*$`
* Blocks (`blocks` keys) must match: `^_[a-z][a-z0-9_]*$`
* Overlap forbidden: a name cannot appear in both `variables` and `blocks`.

### Path consistency rules (mandatory)

For a prompt file at:
`src/llm/prompts/<id>/<version>.md`

* `frontmatter.id` MUST equal `<id>`
* `frontmatter.version` MUST equal `<version>`
* No extra nesting is allowed (exactly two path components under root).

## 2.2 Frontmatter JSON (Includes)

Includes are stored under:
`src/llm/prompts/_includes/<name>/<version>.md`

Includes use the same frontmatter schema, but recommended:

* `variables: []`
* no `blocks`
* `template_engine` optional (defaults to simple).
  Includes are merged as raw text; see composition rules.

## 2.3 Body format

Role sections are delimited by Markdown headings:

* `# system`
* `# user`
* `# assistant` (optional)

### Requirements

* Prompt must contain at least `# system` and `# user`.
* Section headings must be exactly `# <role>` (single `#`), case-insensitive role.

### Variables in content

* For `simple` engine: only `{{name}}` tokens are recognized.
* For `jinja2_sandbox`: full Jinja2 syntax is allowed.

Blocks (enrichment slots) must be referenced by their underscore name:

* `{{_rag_context}}`

---

# 3) Composition Rules (Includes)

## 3.1 Include reference format

`includes: ["policy@v3", "style@v2"]`

Resolution:

* `policy@v3` resolves to: `src/llm/prompts/_includes/policy/v3.md`

## 3.2 Merge strategy

Includes are parsed into role sections too.
For each role present in an include, concatenate into the target prompt role content as:

`<include_role_content>\n\n<original_role_content>`

Includes are applied in the order listed.

## 3.3 Include validation

* Missing include file is a compiler error.
* Include files may omit some roles; only present roles are merged.

---

# 4) Variables, Blocks, and Strictness Rules

## 4.1 Definitions

* **Variables**: required inputs that the caller must provide (`frontmatter.variables`).
* **Blocks**: enrichment slots (optional or required) intended to be filled by middleware or caller (`frontmatter.blocks` keys).

## 4.2 Declared names

Declared names = `variables ∪ blocks.keys`.

## 4.3 Strict declared/used checks (compiler)

After includes are merged:

* Every referenced name must be declared.
* Every declared name must be referenced at least once in the merged prompt content.

Meaning:

* If a name is in `variables` or `blocks`, it must appear in the body.
* If the body uses `{{x}}` (or Jinja2 references `x`), `x` must be declared.

## 4.4 Separation rule

A name cannot appear in both `variables` and `blocks`. This is a compiler error.

## 4.5 Underscore rule

Any referenced name starting with `_` must be a block (must exist in `blocks`). If not, compiler error.

---

# 5) Template Engines

## 5.1 Engine selection

Each prompt chooses engine with `template_engine`:

* default: `"simple"`
* optional: `"jinja2_sandbox"`

The engine applies to all role sections after include merge.

## 5.2 Simple engine

* Only supports `{{var}}` replacement (no logic).
* Missing variables should never occur due to validation; renderer may replace missing with `""` but runtime strict mode should prevent missing required vars.

## 5.3 Jinja2 engine (sandboxed)

* Use `jinja2.sandbox.SandboxedEnvironment`
* Must configure:

  * `undefined=StrictUndefined` (missing var raises)
  * `autoescape=False`
  * `trim_blocks=True`, `lstrip_blocks=True`
* Lock down environment:

  * `env.globals = {}`
  * `env.filters = {}`
  * `env.tests = {}`
  * Do not expose `range`, `cycler`, etc. unless explicitly approved.
* Rendering uses `.from_string(template).render(**values)`.

## 5.4 Compiler variable extraction for validation

* For `simple`: extract referenced vars via regex for `{{name}}`.
* For `jinja2_sandbox`: parse template AST and extract undeclared vars via `jinja2.meta.find_undeclared_variables`.

  * This must be done on the *merged* role content (includes applied).
  * Any names found must be within declared names, or compiler error.
  * If Jinja2 meta finds names that are environment-provided globals, those must be disallowed by not providing them. (Preferred: allow none.)

---

# 6) Compiler

## 6.1 Inputs

* Source root: `src/llm/prompts`
* Compile all `*.md` excluding `_includes/**`.

## 6.2 Outputs

Write:

* `dist/llm_prompts/manifest.json`

## 6.3 Manifest schema (JSON)

Top-level:

```json
{
  "schema_version": 1,
  "prompts": [ ... ]
}
```

Each prompt entry:

```json
{
  "id": "planner",
  "version": "v1",
  "metadata": {...},
  "template_engine": "simple",
  "variables": ["question", "evidence", "_rag_context", "_tool_hints"],
  "blocks": {
    "_rag_context": {"optional": true, "default": ""},
    "_tool_hints":  {"optional": true, "default": ""}
  },
  "messages": [
    {"role":"system","content":"..."},
    {"role":"user","content":"..."},
    {"role":"assistant","content":"..."}
  ],
  "hash": "sha256"
}
```

Notes:

* `variables` in manifest = union of required vars + block names (sorted).
* Persist `blocks` for runtime defaults.
* Persist `template_engine` so runtime knows how to render.

## 6.4 Duplicate detection (compiler)

Compiler must fail if two prompt files produce the same `(id, version)`.

## 6.5 Hashing

Compute `hash = sha256(canonical_json)` where canonical JSON includes:

* id, version, metadata, template_engine
* variables list
* blocks (as JSON)
* messages (role+content)

Canonicalization:

* JSON sort keys
* stable separators
* UTF-8

## 6.6 CLI

Provide a CLI entry point:

* `compile-prompts --src src/llm/prompts --out dist/llm_prompts/manifest.json`
  Exit non-zero with clear error messages on any validation failure.

---

# 7) Runtime

## 7.1 Load

Runtime loads manifest once into memory:

* Map `(id, version)` → prompt
* Track latest version per id (default can be lexicographic; semver optional)

## 7.2 Strict input validation at render-time

Expose `PromptRegistry(strict_inputs=True)` default.

Given a compiled prompt:

* declared blocks = `prompt.blocks.keys`
* required vars = `prompt.variables - declared_blocks`

Validation rules when `strict_inputs=True`:

* Missing required vars → error
* Extra vars (not in required vars) → error
* Extra blocks (not in declared blocks) → error

Values:

* Convert values to strings (None → `""`, non-str → `str(v)`) OR require strings strictly (choose one; recommended: convert but keep keys strict).

## 7.3 Block defaults

Before enrichment:

* For each block in `prompt.blocks`:

  * if missing and optional=true → set default (default may be `""`)
  * if missing and optional=false → error

## 7.4 Enrichment pipeline (middleware)

A pipeline of functions:

`enricher(prompt, vars, blocks) -> dict[str,str]`

Execution:

* Start with blocks after defaults applied
* Apply enrichers sequentially; each can add/override blocks
* After enrichment, in strict mode, ensure no new block keys were introduced beyond declared blocks.

## 7.5 Render

Merge values:

* `values = {**vars, **blocks}`

Then render each message content using the prompt’s engine:

* `simple`: render_simple(content, values)
* `jinja2_sandbox`: render_jinja2(content, values) (StrictUndefined)

Return:
`[{role, content}, ...]` preserving order system, user, assistant (if present).

---

# 8) Error Handling

## 8.1 Compiler errors

Raise/exit with:

* file path
* short reason
* relevant details (missing var names, duplicate sources, bad naming)

## 8.2 Runtime errors

Raise:

* `PromptNotFound` for missing prompt id/version
* `PromptInputError` for missing/extra vars/blocks or missing required block
* Jinja2 rendering errors should surface (missing var etc.) with prompt id/version context

---

# 9) Example Prompt (compliant)

`src/llm/prompts/planner/v1.md`

```md
---
{
  "id": "planner",
  "version": "v1",
  "template_engine": "simple",
  "metadata": { "owner": "core", "intent": "tool_planning", "tools": ["tool.a"] },
  "variables": ["question", "evidence"],
  "includes": ["policy@v3", "style@v2"],
  "blocks": {
    "_rag_context": { "optional": true, "default": "" },
    "_tool_hints":  { "optional": true, "default": "" }
  }
}
---
# system
You are a planning assistant. Return steps and assumptions.

# user
Question:
{{question}}

Context:
{{_rag_context}}

Evidence:
{{evidence}}

Tool hints:
{{_tool_hints}}
```

---

# 10) Jinja2 Example Prompt (compliant)

`src/llm/prompts/router/v1.md`

```md
---
{
  "id": "router",
  "version": "v1",
  "template_engine": "jinja2_sandbox",
  "metadata": { "owner": "core" },
  "variables": ["question"],
  "blocks": {
    "_rag_context": { "optional": true, "default": "" }
  }
}
---
# system
You route requests.

# user
Question: {{ question }}

{% if _rag_context %}
Context:
{{ _rag_context }}
{% endif %}
```

---

# 11) Implementation Checklist

## Compiler

* [ ] Walk tree, gather prompt files (exclude `_includes`)
* [ ] Parse frontmatter JSON + markdown body
* [ ] Enforce path/id/version match and exact nesting
* [ ] Duplicate id@version detection
* [ ] Resolve includes and merge by role
* [ ] Extract referenced vars based on engine (regex vs jinja2 meta)
* [ ] Enforce naming conventions
* [ ] Enforce separation (no overlap, underscore vars must be blocks)
* [ ] Enforce declared↔used strictness
* [ ] Emit manifest with stable hash

## Runtime

* [ ] Load manifest into PromptRegistry
* [ ] Strict input validation (required vars, extras)
* [ ] Apply block defaults
* [ ] Apply enrichment pipeline
* [ ] Render messages per engine
* [ ] Raise informative errors

---

# 12) Security Notes (Jinja2)

* MUST use SandboxedEnvironment + StrictUndefined
* MUST clear globals/filters/tests unless explicitly allowed
* Do not expose Python objects, modules, or helper functions by default

---

If you want, I can also include a short “developer README” section (how to add a prompt, how to compile, how to call registry) in the same spec so it’s ready to drop into your repo.
