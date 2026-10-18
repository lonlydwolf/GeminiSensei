# GeminiSensei sidecar

The Python FastAPI backend belongs to a completed learning project retired from active development. There is no ongoing support or feature roadmap. Read the [project status and limitations](../README.md#known-limitations) before trying a historical release or live API setup.

## Responsibilities

- Call Gemini through the `google-genai` SDK.
- Run LangGraph teacher, reviewer and orchestrator workflows.
- Generate and persist roadmaps and code-review records.
- Store structured data through SQLAlchemy/SQLite and retain agent checkpoints separately.
- Serve local authenticated HTTP endpoints and streaming chat responses to React.

The [architecture](../docs/ARCHITECTURE.md) explains process startup, the Tauri connection-discovery bridge and direct frontend HTTP requests.

## Historical backend-only workflow

Prerequisites are uv and Python 3.12 or later. From this directory:

```bash
uv sync --frozen
uv run python main.py
```

Alternatively, `bun run sidecar:dev` starts the backend from the repository root. Standalone startup prints a random localhost port and session token; it does not automatically connect a separate frontend. Tauri normally relays those details to React.

Live features require a Gemini key. The settings endpoint's verification model is obsolete, so these commands do not establish working onboarding. Starting the application can initialize local databases; inspect it with disposable application data when experimenting.

The backend test suite covers APIs, agents, services and persistence. See the [development notes](../CONTRIBUTING.md#working-in-a-fork) for isolation requirements. The 104 passing tests reported in the project README refer to the dated October 2026 offline review of commit `c2131c6`, not current live API or packaged-runtime validation.
