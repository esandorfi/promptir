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

## Quick Start

### 1. Install Backend Dependencies

```bash
cd ui
pip install -e .
```

### 2. Install Frontend Dependencies

```bash
cd ui/frontend
npm install
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API key
```

### 4. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd ui
uvicorn backend.server:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd ui/frontend
npm run dev
```

Open http://localhost:5173

## Configuration

### Sessions

Edit `ui/data/sessions.json` to configure available prompt collections:

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
| `PROMPTIR_SESSIONS_PATH` | Path to sessions config | `ui/data/sessions.json` |
| `PROMPTIR_TESTCASES_DIR` | Directory for test cases | `ui/data/testcases` |

## Architecture

```
ui/
├── backend/          # FastAPI server
│   ├── server.py     # Main app
│   ├── config.py     # Settings
│   ├── schemas.py    # Pydantic models
│   ├── routes/       # API endpoints
│   └── services/     # Business logic
├── frontend/         # React + Vite
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── hooks/        # React Query hooks
│   │   ├── stores/       # Zustand state
│   │   └── lib/          # Utilities
│   └── package.json
└── data/
    ├── sessions.json     # Session config
    └── testcases/        # Saved test cases
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions` | List sessions |
| GET | `/api/sessions/{id}/prompts` | List prompts |
| GET | `/api/sessions/{id}/prompts/{pid}/{v}/source` | Get source |
| PUT | `/api/sessions/{id}/prompts/{pid}/{v}` | Update prompt |
| POST | `/api/sessions/{id}/compile` | Compile prompts |
| POST | `/api/sessions/{id}/render` | Render prompt |
| POST | `/api/infer` | Run LLM inference |
| GET | `/api/sessions/{id}/prompts/{pid}/diff` | Version diff |

## Development

### Build for Production

```bash
cd ui/frontend
npm run build
```

The built files will be served by FastAPI automatically.

### Run with Single Command

```bash
cd ui
uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000
