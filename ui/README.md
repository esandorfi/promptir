# promptir Workbench

A minimal, full-screen UI for managing prompt manifests.

## Features

- **Session-based**: Switch between different prompt collections
- **Structured editing**: Form-based frontmatter, CodeMirror for templates
- **Live validation**: Real-time Jinja syntax checking and variable validation
- **Preview**: Render prompts with test inputs
- **LLM inference**: Test prompts with OpenAI-compatible APIs
- **Test cases**: Save and load test inputs
- **Version diff**: Compare prompt versions
- **Dark mode**: System preference detection with manual toggle
- **Keyboard shortcuts**: Full keyboard navigation

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Node.js](https://nodejs.org/) 18+ and npm

### Installation

```bash
cd ui

# Install all dependencies (backend + frontend)
make install

# Or manually:
uv sync --dev
cd frontend && npm install
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your API key (optional, for LLM inference)
```

### Development

```bash
# Start both servers (backend on :8000, frontend on :5173)
make dev

# Or run separately:
make dev-backend   # Backend only
make dev-frontend  # Frontend only
```

Open http://localhost:5173

## Docker

### Build and Run

```bash
# Build the image
make docker-build

# Run the container
export OPENAI_API_KEY=your-key-here
make docker-run

# Or manually:
docker build -t promptir-ui .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/../data:/app/data:ro \
  promptir-ui
```

Open http://localhost:8000

### Docker Compose (optional)

```yaml
version: '3.8'
services:
  promptir-ui:
    build: ./ui
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data:ro
```

## Configuration

### Sessions

Edit `data/sessions.json` to configure available prompt collections:

```json
{
  "sessions": [
    {
      "id": "my-prompts",
      "name": "My Prompts",
      "manifest_path": "path/to/manifest.json",
      "prompts_dir": "path/to/prompts"
    }
  ]
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API key for LLM inference | - |
| `OPENAI_BASE_URL` | OpenAI-compatible API endpoint | `https://api.openai.com/v1` |
| `PROMPTIR_SESSIONS_PATH` | Path to sessions config | `data/sessions.json` |
| `PROMPTIR_TESTCASES_DIR` | Directory for test cases | `data/testcases` |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/⌘ + S` | Save changes |
| `Ctrl/⌘ + B` | Compile prompts |
| `Ctrl/⌘ + P` | Toggle preview panel |
| `Ctrl/⌘ + Shift + D` | Toggle dark mode |
| `Shift + ?` | Show shortcuts help |
| `Escape` | Close modals |

## Development

### Available Commands

```bash
make help        # Show all commands

# Setup
make install     # Install all dependencies

# Development
make dev         # Start both servers
make dev-backend # Backend only
make dev-frontend # Frontend only

# Quality
make lint        # Run linters (ruff + eslint)
make format      # Format code (ruff + prettier)
make typecheck   # Type check (pyright + tsc)
make test        # Run tests (pytest + vitest)
make check       # Run all checks

# Build
make build       # Build frontend for production
make clean       # Clean build artifacts
```

### Project Structure

```
ui/
├── backend/              # FastAPI server
│   ├── server.py         # Main app + static file serving
│   ├── config.py         # Settings (pydantic-settings)
│   ├── schemas.py        # Pydantic models
│   ├── routes/           # API endpoints
│   │   ├── sessions.py   # Session management
│   │   ├── prompts.py    # Prompt CRUD
│   │   ├── compile.py    # Compilation
│   │   ├── infer.py      # LLM inference
│   │   └── testcases.py  # Test case management
│   ├── services/         # Business logic
│   │   ├── prompt_service.py
│   │   └── diff_service.py
│   └── tests/            # pytest tests
├── frontend/             # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── hooks/        # React Query + custom hooks
│   │   ├── stores/       # Zustand state
│   │   ├── lib/          # Utilities + CodeMirror setup
│   │   └── types/        # TypeScript types
│   └── __tests__/        # Vitest tests
├── data/
│   ├── sessions.json     # Session configuration
│   └── testcases/        # Saved test cases
├── Dockerfile            # Production container
├── Makefile              # Development commands
└── pyproject.toml        # Python config (uv)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/sessions` | List sessions |
| GET | `/api/sessions/{id}` | Get session details |
| GET | `/api/sessions/{id}/prompts` | List prompts |
| GET | `/api/sessions/{id}/prompts/{pid}/{v}` | Get prompt |
| GET | `/api/sessions/{id}/prompts/{pid}/{v}/source` | Get source |
| PUT | `/api/sessions/{id}/prompts/{pid}/{v}` | Update prompt |
| POST | `/api/sessions/{id}/prompts` | Create prompt |
| DELETE | `/api/sessions/{id}/prompts/{pid}/{v}` | Delete prompt |
| POST | `/api/sessions/{id}/compile` | Compile prompts |
| POST | `/api/sessions/{id}/validate` | Validate prompts |
| POST | `/api/sessions/{id}/render` | Render prompt |
| POST | `/api/infer` | Run LLM inference |
| GET | `/api/infer/models` | List available models |
| GET | `/api/sessions/{id}/prompts/{pid}/diff` | Version diff |
| GET | `/api/sessions/{id}/prompts/{pid}/{v}/testcases` | List test cases |
| POST | `/api/sessions/{id}/prompts/{pid}/{v}/testcases` | Create test case |

## Tech Stack

**Backend:**
- FastAPI + Pydantic
- OpenAI SDK (for inference)
- uv (package management)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- TanStack Query (data fetching)
- Zustand (state management)
- CodeMirror 6 (editor)
- Tailwind CSS (styling)

**Testing:**
- pytest + httpx (backend)
- Vitest + Testing Library (frontend)

**Linting/Formatting:**
- ruff (Python)
- ESLint + Prettier (TypeScript)
- pyright + tsc (type checking)
