# GeminiSensei

**Completed learning project · retired from active development**

GeminiSensei is an experimental desktop application for AI-assisted programming education, built with Tauri, React and a Python FastAPI sidecar. It explored generated learning roadmaps, Socratic tutoring and code-review feedback through Gemini and LangGraph.

I started it for a competition because I felt a useful AI education system was missing. Building it taught me about desktop/backend integration and, eventually, about choosing a product format that fits the learning workflow. That exploration continued in [Faculty](https://github.com/lonlydwolf/skills/tree/main/skills/faculty).

The repository is retained as a record of that work. There is no active roadmap or ongoing support commitment. Historical downloads have known defects; they should not be treated as a working, supported release.

- [Case study: motivation, contribution and lessons](docs/CASE_STUDY.md)
- [Architecture and data flow](docs/ARCHITECTURE.md)
- [Historical development notes](CONTRIBUTING.md)

## What was implemented

- A React/TypeScript interface for settings, learning roadmaps and streaming chat.
- A Tauri desktop shell that starts and discovers a local Python sidecar.
- FastAPI endpoints for roadmap generation, chat, code review and settings.
- LangGraph teacher, reviewer and orchestrator workflows, plus a roadmap-generation service.
- SQLite persistence, Alembic migrations, typed schemas and automated backend/frontend tests.

The stack includes Tailwind CSS, TanStack Query, SQLAlchemy and Google's `google-genai` SDK. Dependencies in the historical manifests also include experiments such as LanceDB; semantic retrieval is not an implemented application feature. Socratic behavior is prompt-based and does not guarantee factual accuracy or enforce mastery of a subject.

## Known limitations

A review on **18 October 2026**, at source commit [`c2131c6`](https://github.com/lonlydwolf/GeminiSensei/commit/c2131c6e4852e934047d06a046b7c0dbabf7e2f6), found:

- **Release packaging:** the inspected `v0.1.1` macOS ARM64 artifact lacks application migration/configuration files and the teacher, reviewer and orchestrator modules. A successful build did not establish a working installation. Other platform artifacts were not inspected.
- **Onboarding:** API-key verification hardcodes `gemini-2.0-flash-lite`, which Google [shut down on 1 June 2026](https://ai.google.dev/gemini-api/docs/deprecations). New-key setup needs updating before live use.
- **Streaming:** the frontend treats network chunks as complete events, trims meaningful spaces and can drop numeric text. Split or combined events can expose framing in chat output.
- **Conversation context:** checkpoints retain messages, but the teacher's response prompt includes only the latest message and lesson metadata. Stored history does not currently provide full conversational context to generation.
- **Educational claims:** Google Search is not enabled by the teacher generation call, and guardrail failures permit generation to continue. Earlier claims of mandatory verification and guaranteed gatekeeping overstated the implementation.

The source default `gemini-3-pro-preview` is also historical: Google's [9 March 2026 release notes](https://ai.google.dev/gemini-api/docs/changelog#march-9-2026) describe its retirement and redirection to `gemini-3.1-pro-preview`. That is distinct from the shut-down onboarding model.

During that review, **104 backend tests passed** with frozen dependencies on Python 3.14.8, a temporary application-data directory and external network access blocked. This was an offline source-level result, not verification of live Gemini calls or a packaged desktop application. The full frontend suite and Rust build were not rerun. See the [case study](docs/CASE_STUDY.md#what-the-later-review-showed) for the implications.

## Historical development setup

These instructions describe the existing source workflow for study or a fork; they do not resolve the limitations above.

Prerequisites:

- [Bun](https://bun.sh/) for JavaScript dependencies and scripts, and Node.js for the development sidecar setup script.
- [uv](https://docs.astral.sh/uv/) and Python 3.12 or later for the backend.
- Rust/Cargo and the platform dependencies listed in [Tauri's prerequisites](https://v2.tauri.app/start/prerequisites/).
- A Gemini API key for live AI features, subject to repairing the obsolete onboarding verification path.

From the repository root:

```bash
bun install --frozen-lockfile
cd sidecar
uv sync --frozen
cd ..
bun run tauri:dev
```

The development sidecar proxy is a shell script on macOS/Linux. Its Windows branch writes a batch shim with an `.exe` name; Windows development startup has not been established as working. See the [sidecar notes](sidecar/README.md) for backend-only inspection.

### Scripts

| Script            | Existing behavior                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------- |
| `dev`             | Start the Vite frontend server.                                                             |
| `build`           | Typecheck and build the frontend.                                                           |
| `tauri:dev`       | Generate the development sidecar proxy and start Tauri.                                     |
| `tauri:build`     | Package the sidecar and build the desktop application; known packaging defects remain.      |
| `sidecar:dev`     | Run the Python backend through uv.                                                          |
| `sidecar:install` | Run `uv sync` in the sidecar directory.                                                     |
| `test`            | Run frontend tests with Vitest.                                                             |
| `lint`            | Run ESLint on the frontend/tooling source.                                                  |
| `format`          | Apply Prettier formatting.                                                                  |
| `validate`        | Run frontend lint/types/tests and backend Ruff lint/format, basedpyright and pytest checks. |
| `docs:build`      | Generate the OpenAPI specification.                                                         |

Backend tests include settings and reset operations; use isolated application data when studying or extending them. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache 2.0](LICENSE). Historical releases are available under [Releases](https://github.com/lonlydwolf/GeminiSensei/releases); the `v0.1.1` tag still contains application manifests labeled `0.1.0`.
