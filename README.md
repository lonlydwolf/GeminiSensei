# GeminiSensei (The Academic Practitioner)

[![CI](https://github.com/lonlydwolf/GeminiSensei/actions/workflows/ci.yml/badge.svg)](https://github.com/lonlydwolf/GeminiSensei/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version: 0.1.0](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/lonlydwolf/GeminiSensei/releases)

**GeminiSensei** is a desktop-native AI Engineering Lead designed to enforce rigorous computer science education through a "Strict Protocol Loop." Unlike passive chatbots that simply answer questions, GeminiSensei actively manages a student's development.

It refuses to hallucinate by mandating live Google Search verification, refuses to spoon-feed code by enforcing strict Spec-First development, and actively blocks progress using "Gatekeeping" logic until specific theoretical foundations are proven. It is not just a tutor; it is a Guardian of Code Quality.

## Key Features

*   **Personalized Learning Roadmaps**: AI-generated curriculum based on user goals and background.
*   **AI-Powered Chat Interface**: Context-aware tutoring with streaming responses.
*   **Code Review System**: Automated feedback on student code from a dedicated code reviewer agent.
*   **Multi-Agent Architecture**: An orchestrator coordinates workflows between teaching, code review, and roadmap creation agents.
*   **Settings Management**: Configure your Gemini API key and user preferences.

## Technology Stack

### Frontend
*   **Tauri 2.0**: For building desktop applications with web technologies.
*   **React 18**: A JavaScript library for building user interfaces.
*   **TypeScript**: A typed superset of JavaScript that compiles to plain JavaScript.
*   **Vite**: A modern frontend build tool.
*   **Tailwind CSS**: A utility-first CSS framework.
*   **TanStack Query**: For data fetching and state management.

### Backend (Sidecar)
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
*   **Google Gemini AI**: Powering the AI capabilities.
*   **LangGraph**: For building stateful, multi-agent applications.
*   **LanceDB**: For vector storage and semantic search.
*   **SQLite**: For local data storage.

## Development Setup

To get started with development, you'll need to have [Bun](https://bun.sh/) installed.

1.  **Install dependencies:**
    ```bash
    bun install
    bun run sidecar:install
    ```

2.  **Run the application in development mode:**
    ```bash
    bun run tauri:dev
    ```

### Available Scripts

| Script                | Description                                         |
| --------------------- | --------------------------------------------------- |
| `dev`                 | Start the Vite dev server for the frontend.         |
| `build`               | Build the frontend for production.                  |
| `tauri:dev`           | Start the full application in development mode.     |
| `tauri:build`         | Build the production-ready application.             |
| `sidecar:dev`         | Run the Python backend sidecar.                     |
| `sidecar:install`     | Install Python dependencies.                        |
| `test`                | Run frontend tests.                                 |
| `lint`                | Lint the TypeScript and Python code.                |
| `format`              | Format the code.                                    |
| `validate`            | Run all validation checks (lint, format, typecheck).|
| `docs:build`          | Generate OpenAPI documentation.                     |

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.