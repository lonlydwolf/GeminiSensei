# Architecture: GeminiSensei

## Overview

GeminiSensei is a cross-platform desktop application designed to tutor students in programming using a Socratic approach.

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, TanStack Query, Tailwind CSS.
- **Desktop Shell**: Tauri 2.0 (Rust).
- **Backend (Sidecar)**: FastAPI (Python 3.14), SQLAlchemy (Async), LangGraph, Gemini API.
- **Persistence**: SQLite (via SQLAlchemy for roadmaps, via SqliteSaver for LangGraph checkpoints).

## Data Flow

1. **User Request**: React Frontend -> Tauri Command -> FastAPI Sidecar.
2. **Intelligence**: FastAPI Sidecar -> Gemini API (gemini-2.0-flash-exp).
3. **State Management**: LangGraph manages the "Strict Teacher" state, persisted in `checkpoints.db`.
4. **Data Layer**: Structured roadmap data is stored in `roadmaps.db`.

## Socratic Agent (LangGraph)

The agent is designed with nodes for:

- **Guardrail**: Identifies requests for direct code.
- **Socratic Engine**: Formulates questions based on Gemini's analysis.
- **Context Management**: Injects lesson metadata and documentation links.
