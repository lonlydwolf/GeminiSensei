# GeminiSensei Sidecar

This directory contains the Python-based backend for GeminiSensei, which runs as a sidecar process to the main Tauri application.

## Overview

The sidecar is a FastAPI server responsible for:

*   Interacting with the Google Gemini AI API.
*   Managing the multi-agent system using LangGraph.
*   Handling business logic for learning roadmaps, code reviews, and chat interactions.
*   Persisting data to a local SQLite database.

## Running the Sidecar

To run the sidecar in development mode, use the following command from the root of the project:

```bash
bun run sidecar:dev
```
