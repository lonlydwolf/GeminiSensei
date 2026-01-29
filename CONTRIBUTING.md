# Contributing to GeminiSensei

## Version Control

We use `jj` (Jujutsu) for development, but contributors are welcome to use `git`.

- **JJ Workflow**: Work on the `develop` bookmark.
- **Git Workflow**: Use the `develop` branch for PRs.

## Commit Messages

Follow conventional commits:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `chore:` for maintenance
- `refactor:` for code changes that neither fix a bug nor add a feature

## Development Standards

- **Small Files**: Keep files under 800 lines.
- **Async First**: Use `async/await` for all I/O in Python and TypeScript.
- **Type Safety**: Use Pydantic (Python) and TypeScript interfaces strictly.
- **Strict Teaching**: AI assistant must not write full solutions; use Socratic questioning.
