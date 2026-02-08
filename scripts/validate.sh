#!/bin/bash
set -e

echo "🚀 Starting validation..."

# 1. Frontend Checks
echo "--- Frontend: Linting ---"
bun run lint

echo "--- Frontend: Typechecking ---"
bun run typecheck

echo "--- Frontend: Testing ---"
bun run test

# 2. Backend Checks
echo "--- Backend: Linting ---"
cd sidecar
uv run ruff check .

echo "--- Backend: Formatting Check ---"
uv run ruff format --check .

echo "--- Backend: Typechecking ---"
uv run basedpyright .

echo "--- Backend: Testing ---"
uv run pytest

echo "✅ Validation successful!"
