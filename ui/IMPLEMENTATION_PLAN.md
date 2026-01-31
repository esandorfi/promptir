# Prompt Workbench - Implementation Plan

## Overview

A minimal, full-screen UI for managing prompt manifests with:
- Structured frontmatter editing (forms)
- CodeMirror 6 template editor with Jinja highlighting
- Live preview with test inputs
- LLM inference testing (OpenAI-compatible API)
- Test case persistence
- Version diff viewer
- Session-based manifest loading

---

## Architecture

```
ui/
├── backend/
│   ├── __init__.py
│   ├── server.py              # FastAPI app entry
│   ├── config.py              # Settings & session config
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── sessions.py        # Session/manifest endpoints
│   │   ├── prompts.py         # CRUD for prompts
│   │   ├── compile.py         # Compilation endpoint
│   │   ├── infer.py           # LLM inference proxy
│   │   └── testcases.py       # Test case management
│   ├── schemas.py             # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── prompt_service.py  # Business logic
│       └── diff_service.py    # Version diff logic
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx           # Entry point
│   │   ├── App.tsx            # Root component
│   │   ├── api/
│   │   │   └── client.ts      # API client
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Panel.tsx
│   │   │   ├── prompts/
│   │   │   │   ├── PromptList.tsx
│   │   │   │   ├── PromptEditor.tsx
│   │   │   │   ├── MetadataForm.tsx
│   │   │   │   ├── InputsForm.tsx
│   │   │   │   └── TemplateEditor.tsx
│   │   │   ├── preview/
│   │   │   │   ├── PreviewPanel.tsx
│   │   │   │   ├── TestInputs.tsx
│   │   │   │   └── RenderedMessages.tsx
│   │   │   ├── inference/
│   │   │   │   ├── InferencePanel.tsx
│   │   │   │   └── ResponseViewer.tsx
│   │   │   ├── testcases/
│   │   │   │   ├── TestCaseList.tsx
│   │   │   │   └── TestCaseForm.tsx
│   │   │   ├── diff/
│   │   │   │   └── VersionDiff.tsx
│   │   │   └── ui/            # shadcn components
│   │   ├── hooks/
│   │   │   ├── usePrompts.ts
│   │   │   ├── useSession.ts
│   │   │   ├── useInference.ts
│   │   │   └── useTestCases.ts
│   │   ├── lib/
│   │   │   ├── codemirror/
│   │   │   │   ├── setup.ts
│   │   │   │   ├── jinja-highlight.ts
│   │   │   │   └── autocomplete.ts
│   │   │   ├── validation.ts
│   │   │   └── utils.ts
│   │   ├── stores/
│   │   │   └── workbench.ts   # Zustand store
│   │   └── types/
│   │       ├── prompt.ts
│   │       ├── session.ts
│   │       └── testcase.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── data/
│   ├── sessions.json          # Session → manifest mapping
│   └── testcases/             # Test cases per prompt
│       └── {session_id}/
│           └── {prompt_id}_{version}.json
│
├── pyproject.toml             # Backend dependencies
├── package.json               # Root scripts (optional)
└── README.md
```

---

## Data Models

### Session Configuration (`data/sessions.json`)

```json
{
  "sessions": [
    {
      "id": "demo-docs",
      "name": "Document Analysis",
      "manifest_path": "data/demo_datasets/document_analysis/manifest.json",
      "prompts_dir": "data/demo_datasets/document_analysis/prompts"
    },
    {
      "id": "demo-local",
      "name": "Local Operations",
      "manifest_path": "data/demo_datasets/local_operations/manifest.json",
      "prompts_dir": "data/demo_datasets/local_operations/prompts"
    },
    {
      "id": "main",
      "name": "Main Prompts",
      "manifest_path": "dist/llm_prompts/manifest.json",
      "prompts_dir": "src/llm/prompts"
    }
  ]
}
```

### Test Case Format (`data/testcases/{session}/{prompt_id}_{version}.json`)

```json
{
  "prompt_id": "document_analyze_single",
  "version": "v1",
  "test_cases": [
    {
      "id": "tc-001",
      "name": "Basic document analysis",
      "created_at": "2025-01-30T10:00:00Z",
      "inputs": {
        "vars": {
          "question": "What is this document about?",
          "document": "..."
        },
        "blocks": {
          "_rag_context": "Additional context...",
          "_tool_hints": ""
        }
      },
      "last_response": {
        "content": "This document discusses...",
        "model": "gpt-4",
        "tokens_in": 234,
        "tokens_out": 156,
        "latency_ms": 1200,
        "timestamp": "2025-01-30T10:05:00Z"
      }
    }
  ]
}
```

---

## Backend API Specification

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions` | List all available sessions |
| GET | `/api/sessions/{id}` | Get session details + manifest |

### Prompts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions/{sid}/prompts` | List prompts in session |
| GET | `/api/sessions/{sid}/prompts/{id}` | Get prompt (latest version) |
| GET | `/api/sessions/{sid}/prompts/{id}/{version}` | Get specific version |
| GET | `/api/sessions/{sid}/prompts/{id}/{version}/source` | Get raw source file |
| PUT | `/api/sessions/{sid}/prompts/{id}/{version}` | Update prompt source |
| POST | `/api/sessions/{sid}/prompts` | Create new prompt |
| DELETE | `/api/sessions/{sid}/prompts/{id}/{version}` | Delete prompt version |

### Compilation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions/{sid}/compile` | Compile session prompts |
| POST | `/api/sessions/{sid}/validate` | Validate without compiling |
| POST | `/api/sessions/{sid}/render` | Render prompt with inputs |

### Inference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/infer` | Run LLM inference |
| GET | `/api/infer/models` | List available models |

### Test Cases

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions/{sid}/prompts/{id}/{v}/testcases` | List test cases |
| POST | `/api/sessions/{sid}/prompts/{id}/{v}/testcases` | Create test case |
| PUT | `/api/sessions/{sid}/prompts/{id}/{v}/testcases/{tc}` | Update test case |
| DELETE | `/api/sessions/{sid}/prompts/{id}/{v}/testcases/{tc}` | Delete test case |

### Diff

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions/{sid}/prompts/{id}/diff?v1=v1&v2=v2` | Get diff between versions |

---

## Frontend Components Detail

### 1. Layout (Full Screen, Minimal)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [Session: Document Analysis ▼]                    [Compile] [Settings]  │
├─────────┬───────────────────────────────────────────────────────────────┤
│         │                                                               │
│ PROMPTS │  EDITOR                                                       │
│         │                                                               │
│ ┌─────┐ │  ┌─────────────────────────────────────────────────────────┐  │
│ │     │ │  │                                                         │  │
│ │     │ │  │                                                         │  │
│ │     │ │  │                                                         │  │
│ │     │ │  │                                                         │  │
│ │     │ │  │                                                         │  │
│ └─────┘ │  └─────────────────────────────────────────────────────────┘  │
│         │                                                               │
│         ├───────────────────────────────────────────────────────────────┤
│         │  PREVIEW & TEST                                    [Expand ▲] │
│         │  ┌─────────────────────┬─────────────────────────────────────┐│
│         │  │ Inputs              │ Preview          │ Inference        ││
│         │  └─────────────────────┴─────────────────────────────────────┘│
└─────────┴───────────────────────────────────────────────────────────────┘
```

### 2. Editor Sections (Tabs or Accordion)

```
┌─ planner@v1 ────────────────────────────────── [Save] [Validate] [Diff] ┐
│                                                                         │
│  [Metadata] [Inputs] [Template] [Test Cases]                            │
│  ═══════════════════════════════════════════                            │
│                                                                         │
│  ┌─ Template ─────────────────────────────────────────────────────────┐ │
│  │                                                                    │ │
│  │  Role: [system ▼]  [+ Add Role]                                    │ │
│  │  ┌────────────────────────────────────────────────────────────┐    │ │
│  │  │ You are a planning assistant.                              │    │ │
│  │  │                                                            │    │ │
│  │  │ {{policy}}                                                 │    │ │
│  │  │                                                            │    │ │
│  │  │ Guidelines:                                                │    │ │
│  │  │ - Be concise                                               │    │ │
│  │  │ - Use evidence                                             │    │ │
│  │  └────────────────────────────────────────────────────────────┘    │ │
│  │                                                                    │ │
│  │  Role: [user ▼]                                                    │ │
│  │  ┌────────────────────────────────────────────────────────────┐    │ │
│  │  │ Question: {{question}}                                     │    │ │
│  │  │                                                            │    │ │
│  │  │ {% if _rag_context %}                                      │    │ │
│  │  │ Context:                                                   │    │ │
│  │  │ {{_rag_context}}                                           │    │ │
│  │  │ {% endif %}                                                │    │ │
│  │  │                                                            │    │ │
│  │  │ Evidence: {{evidence}}                                     │    │ │
│  │  └────────────────────────────────────────────────────────────┘    │ │
│  │                                                                    │ │
│  │  ⚠ Warning: '_tool_hints' declared but unused                      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3. Preview Panel

```
┌─ PREVIEW & TEST ──────────────────────────────────────────── [Collapse] ┐
│                                                                         │
│  ┌─ Test Inputs ───────────┐  ┌─ Rendered ─────────────────────────────┐│
│  │                         │  │                                        ││
│  │  question               │  │  ┌─ system ─────────────────────────┐  ││
│  │  ┌─────────────────────┐│  │  │ You are a planning assistant.   │  ││
│  │  │ What is...         ││  │  │                                  │  ││
│  │  └─────────────────────┘│  │  │ Always follow the policy...     │  ││
│  │                         │  │  └──────────────────────────────────┘  ││
│  │  evidence               │  │                                        ││
│  │  ┌─────────────────────┐│  │  ┌─ user ───────────────────────────┐  ││
│  │  │ The document says..││  │  │ Question: What is...             │  ││
│  │  └─────────────────────┘│  │  │                                  │  ││
│  │                         │  │  │ Context:                         │  ││
│  │  _rag_context           │  │  │ Retrieved from vector DB...      │  ││
│  │  ┌─────────────────────┐│  │  │                                  │  ││
│  │  │ Retrieved from...  ││  │  │ Evidence: The document says...   │  ││
│  │  └─────────────────────┘│  │  └──────────────────────────────────┘  ││
│  │                         │  │                                        ││
│  │  [Load Test Case ▼]     │  │  Tokens: ~450                          ││
│  │  [Save as Test Case]    │  │                                        ││
│  └─────────────────────────┘  └────────────────────────────────────────┘│
│                                                                         │
│  ┌─ LLM Inference ──────────────────────────────────────────────────────┐
│  │  Model: [gpt-4 ▼]  Temp: [0.7]  Max: [1024]        [🚀 Run]         │
│  │  ┌────────────────────────────────────────────────────────────────┐  │
│  │  │                                                                │  │
│  │  │  The capital of France is Paris...                             │  │
│  │  │                                                                │  │
│  │  ├────────────────────────────────────────────────────────────────┤  │
│  │  │  ⏱ 1.2s  │  📥 450 tokens  │  📤 89 tokens  │  $0.016          │  │
│  │  └────────────────────────────────────────────────────────────────┘  │
│  └──────────────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────┘
```

### 4. Version Diff Modal

```
┌─ Diff: planner v1 → v2 ──────────────────────────────────────────── [×] ┐
│                                                                         │
│  [v1 ▼] ←→ [v2 ▼]                                                       │
│                                                                         │
│  ┌─ Frontmatter Changes ────────────────────────────────────────────┐   │
│  │  variables:                                                      │   │
│  │  - ["question", "evidence"]                                      │   │
│  │  + ["question", "evidence", "context"]                           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─ Template Changes ───────────────────────────────────────────────┐   │
│  │  # system                                                        │   │
│  │    You are a planning assistant.                                 │   │
│  │  - Be concise and helpful.                                       │   │
│  │  + Be concise, helpful, and accurate.                            │   │
│  │                                                                  │   │
│  │  # user                                                          │   │
│  │    Question: {{question}}                                        │   │
│  │  + Context: {{context}}                                          │   │
│  │    Evidence: {{evidence}}                                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation (Backend + Basic Frontend)

**Backend:**
1. FastAPI app setup with CORS
2. Session configuration loading
3. Prompt listing and reading endpoints
4. Basic validation endpoint

**Frontend:**
1. Vite + React + TypeScript setup
2. Tailwind + shadcn/ui setup
3. Basic layout (sidebar + main panel)
4. Session selector
5. Prompt list component
6. Basic API client

### Phase 2: Editor Core

**Backend:**
1. Prompt update endpoint (write to disk)
2. Prompt creation endpoint
3. Full compilation endpoint
4. Render endpoint (for preview)

**Frontend:**
1. Metadata form (id, version, engine, includes)
2. Inputs form (variables, blocks)
3. CodeMirror 6 integration
4. Jinja syntax highlighting
5. Variable autocomplete
6. Real-time validation display

### Phase 3: Preview & Validation

**Backend:**
1. Enhanced validation (return detailed errors)
2. Render endpoint with error handling

**Frontend:**
1. Test inputs panel
2. Live rendered preview
3. Validation warnings display
4. Token count estimation

### Phase 4: LLM Inference

**Backend:**
1. OpenAI-compatible inference endpoint
2. Model listing (from config)
3. Token counting
4. Cost estimation

**Frontend:**
1. Inference panel
2. Model/parameter selection
3. Response viewer
4. Usage stats display

### Phase 5: Test Cases

**Backend:**
1. Test case CRUD endpoints
2. File-based storage

**Frontend:**
1. Test case list
2. Save current inputs as test case
3. Load test case into inputs
4. Test case naming/management

### Phase 6: Diff & Polish

**Backend:**
1. Diff computation endpoint
2. Version history endpoint

**Frontend:**
1. Version diff modal
2. Side-by-side or unified diff view
3. Polish: keyboard shortcuts, loading states
4. Error boundaries

---

## Technical Details

### CodeMirror 6 Setup

```typescript
// lib/codemirror/setup.ts
import { EditorView, basicSetup } from 'codemirror'
import { markdown } from '@codemirror/lang-markdown'
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language'
import { tags } from '@lezer/highlight'
import { autocompletion } from '@codemirror/autocomplete'

// Custom Jinja highlighting
const jinjaHighlight = HighlightStyle.define([
  { tag: tags.processingInstruction, color: '#22c55e' },  // {{ }}
  { tag: tags.special(tags.variableName), color: '#3b82f6' },  // variable names
])

// Variable autocomplete based on declared vars
function createVariableCompletion(variables: string[]) {
  return autocompletion({
    override: [(context) => {
      const before = context.matchBefore(/\{\{\s*\w*/)
      if (!before) return null
      return {
        from: before.from + 2,
        options: variables.map(v => ({
          label: v,
          type: v.startsWith('_') ? 'property' : 'variable',
          detail: v.startsWith('_') ? 'block' : 'required'
        }))
      }
    }]
  })
}
```

### Jinja Validation (Frontend)

```typescript
// lib/validation.ts
interface ValidationResult {
  errors: ValidationError[]
  warnings: ValidationWarning[]
}

function validateTemplate(
  content: string,
  declaredVars: string[],
  declaredBlocks: string[]
): ValidationResult {
  const errors: ValidationError[] = []
  const warnings: ValidationWarning[] = []

  // Extract used variables
  const simplePattern = /\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}/g
  const used = new Set<string>()
  let match
  while ((match = simplePattern.exec(content))) {
    used.add(match[1])
  }

  // Check for undeclared
  const declared = new Set([...declaredVars, ...declaredBlocks])
  for (const v of used) {
    if (!declared.has(v)) {
      errors.push({
        type: 'undeclared',
        variable: v,
        message: `Undeclared variable: ${v}`
      })
    }
  }

  // Check for unused
  for (const v of declared) {
    if (!used.has(v)) {
      warnings.push({
        type: 'unused',
        variable: v,
        message: `Declared but unused: ${v}`
      })
    }
  }

  return { errors, warnings }
}
```

### OpenAI-Compatible Inference

```python
# backend/routes/infer.py
from openai import OpenAI
from pydantic import BaseModel
import time

class InferRequest(BaseModel):
    messages: list[dict[str, str]]
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1024

class InferResponse(BaseModel):
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_estimate: float | None

@router.post("/api/infer")
async def run_inference(req: InferRequest) -> InferResponse:
    # Uses OPENAI_API_KEY and OPENAI_BASE_URL from env
    client = OpenAI()  # Auto-reads from env

    start = time.perf_counter()
    response = client.chat.completions.create(
        model=req.model,
        messages=req.messages,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )
    latency = int((time.perf_counter() - start) * 1000)

    usage = response.usage
    return InferResponse(
        content=response.choices[0].message.content,
        model=response.model,
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        latency_ms=latency,
        cost_estimate=estimate_cost(req.model, usage)
    )
```

---

## Environment Variables

```bash
# .env (backend)
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1  # Or compatible endpoint

# Optional
PROMPTIR_SESSIONS_PATH=data/sessions.json
PROMPTIR_TESTCASES_DIR=data/testcases
```

---

## Dependencies

### Backend (`ui/pyproject.toml`)

```toml
[project]
name = "promptir-ui"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.109",
    "uvicorn[standard]>=0.27",
    "pydantic>=2.5",
    "openai>=1.10",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.4", "httpx>=0.26"]
```

### Frontend (`ui/frontend/package.json`)

```json
{
  "name": "promptir-workbench",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.0",
    "codemirror": "^6.0.1",
    "@codemirror/lang-markdown": "^6.2.0",
    "@codemirror/autocomplete": "^6.12.0",
    "@codemirror/language": "^6.10.0",
    "@uiw/react-codemirror": "^4.21.0",
    "diff": "^5.1.0",
    "lucide-react": "^0.312.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/diff": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## File Count Estimate

| Directory | Files | Purpose |
|-----------|-------|---------|
| backend/ | ~12 | FastAPI server |
| frontend/src/components/ | ~20 | React components |
| frontend/src/hooks/ | ~5 | Custom hooks |
| frontend/src/lib/ | ~5 | Utilities |
| frontend/src/ | ~5 | Entry, types, stores |
| frontend/ | ~6 | Config files |
| data/ | ~2 | Sessions, testcases |

**Total: ~55 files**

---

## Development Workflow

```bash
# Terminal 1: Backend
cd ui/backend
pip install -e ".[dev]"
uvicorn server:app --reload --port 8000

# Terminal 2: Frontend
cd ui/frontend
npm install
npm run dev  # Vite on port 5173

# Frontend proxies /api/* to localhost:8000
```

---

## Next Steps

1. Confirm this plan aligns with your vision
2. Start with Phase 1 implementation
3. Iterate based on feedback

Ready to proceed?
