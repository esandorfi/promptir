
# promptir

**Compile prompts like code.**

`promptir` is a **local-first prompt compiler and runtime registry** for LLM applications.

Prompts are authored as **versioned Markdown files**, strictly validated, **compiled into a deterministic manifest**, and loaded at runtime as a stable **prompt intermediate representation (IR)**.

No cloud. No UI. No magic.

---

## Why promptir?

Most prompt tooling treats prompts as strings.

`promptir` treats prompts as **source code**.

It gives you:

* **Strict authoring rules** (no undeclared variables, no unused inputs)
* **Versioned prompts** checked into Git
* **Compilation to a stable manifest** (fast, cacheable, hashable)
* **Runtime safety** (no missing or extra inputs)
* **Explicit enrichment slots** for RAG, tools, memory
* **Optional Jinja2 (sandboxed)** for advanced users

If you believe prompts deserve the same rigor as code, `promptir` is for you.

---

## Core Concepts

### Prompt = Source

Prompts live in Git as Markdown with JSON frontmatter.

```
src/llm/prompts/<id>/<version>.md
```

### Manifest = IR

Prompts are compiled into a single `manifest.json`:

* resolved includes
* validated variables
* stable hashes
* ready for fast runtime loading

### Runtime = Registry

At runtime, you load the manifest once and render prompts with **strict validation**.

---

## Installation

```bash
pip install promptir
```

---

## Authoring Prompts

### File layout

```
src/llm/prompts/
  planner/
    v1.md
  _includes/
    policy/
      v3.md
```

---

### Prompt example

```md
---
{
  "id": "planner",
  "version": "v1",
  "metadata": {
    "owner": "core",
    "intent": "tool_planning"
  },
  "variables": ["question", "evidence"],
  "includes": ["policy@v3"],
  "blocks": {
    "_rag_context": { "optional": true, "default": "" },
    "_tool_hints":  { "optional": true, "default": "" }
  }
}
---
# system
You are a planning assistant.

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

## Variables vs Blocks (Important)

### Variables

* Required inputs provided by the caller
* Declared in `variables`
* Naming: `^[a-z][a-z0-9_]*$`

Example:

```json
"variables": ["question", "evidence"]
```

### Blocks

* Enrichment slots (RAG, tools, memory, etc.)
* Declared in `blocks`
* Naming: **must start with `_`**

Example:

```json
"blocks": {
  "_rag_context": { "optional": true, "default": "" }
}
```

### Rules

* A name cannot be both a variable and a block
* Any `{{_name}}` **must** be declared in `blocks`
* Every declared name must be used in the prompt
* Every used name must be declared

Violations are **compile-time errors**.

---

## Includes (Prompt Composition)

Reusable prompt fragments live under `_includes`:

```
src/llm/prompts/_includes/policy/v3.md
```

```md
---
{
  "id": "policy",
  "version": "v3",
  "variables": []
}
---
# system
Follow company policy.
Be concise.
```

Use them in prompts:

```json
"includes": ["policy@v3"]
```

Includes are merged **by role** and resolved at compile time.

---

## Compiling Prompts

Compile all prompts into a manifest:

```bash
promptir compile \
  --src src/llm/prompts \
  --out dist/llm_prompts/manifest.json
```

What the compiler enforces:

* Path ↔ id/version consistency
* No duplicate `id@version`
* Strict variable usage
* Naming conventions
* Include resolution
* Stable hashing

If compilation succeeds, your prompts are valid.

---

## Runtime Usage

### Load the manifest

```python
from promptir import PromptRegistry

registry = PromptRegistry.from_manifest_path(
    "dist/llm_prompts/manifest.json"
)
```

### Render a prompt

```python
rendered = registry.render(
    "planner",
    version="v1",
    vars={
        "question": "How do we deploy safely?",
        "evidence": "Runbook section 3.2"
    },
    blocks={
        "_rag_context": "Relevant docs: /deploy/runbook"
    }
)

for msg in rendered.messages:
    print(msg["role"], msg["content"])
```

### Runtime guarantees

* Missing required vars → error
* Extra vars → error
* Missing required blocks → error
* Extra blocks → error
* Optional blocks get defaults automatically

---

## Enrichment Pipeline

You can inject data programmatically (RAG, tools, telemetry):

```python
from promptir.enrich import EnrichmentPipeline, tool_hints_enricher

registry.set_enrichment_pipeline(
    EnrichmentPipeline([tool_hints_enricher])
)
```

Enrichers:

* receive `(prompt, vars, blocks)`
* return additional blocks
* cannot introduce undeclared block names (strict mode)

---

## Jinja2 Support (Optional)

For advanced users, prompts can opt into **sandboxed Jinja2**:

```json
"template_engine": "jinja2_sandbox"
```

Example:

```md
# user
Question: {{ question }}

{% if _rag_context %}
Context:
{{ _rag_context }}
{% endif %}
```

### Safety

* Uses `SandboxedEnvironment`
* `StrictUndefined` (missing vars raise)
* No globals, filters, or tests by default

### Validation

* Variables are extracted from the Jinja2 AST at compile time
* Undeclared names are compile-time errors

---

## Philosophy

* Prompts are **code**
* Validation belongs at **build time**
* Runtime should be **fast and boring**
* Enrichment must be **explicit**
* No hidden inputs
* No silent failures

---

## When to Use promptir

✅ Large or long-lived LLM systems
✅ Teams with multiple prompt authors
✅ Regulated or safety-critical workflows
✅ Systems using RAG or tools
✅ Git-centric development

❌ One-off scripts
❌ Ad-hoc experimentation
❌ UI-driven prompt tweaking

---

## Roadmap (Non-binding)

* Prompt ABI compatibility checks
* Prompt diffs and migrations
* Typed prompt outputs
* Dev-mode hot reload
* Language-agnostic manifest consumers

---

## Authorship

`promptir` was designed and initially implemented by  
**Emmanuel Sandorfi**, Knowledge AI Senior Software Engineer at **LightOn**,  
in collaboration with **Codex**.

The project reflects practical experience building and operating
production-grade LLM systems, with an emphasis on strict validation,
determinism, and long-term maintainability.


---

## License

MIT


