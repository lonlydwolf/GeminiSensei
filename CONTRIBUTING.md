# Historical development notes

GeminiSensei is a completed learning project retired from active development. There is no active roadmap, ongoing support commitment or expectation of new contributions. The source remains available to study and fork under the [Apache 2.0 license](LICENSE).

For context, start with the [case study](docs/CASE_STUDY.md), [architecture](docs/ARCHITECTURE.md) and [known limitations](README.md#known-limitations). The [README setup instructions](README.md#historical-development-setup) describe the existing workflow and prerequisites; they are not a guarantee that a fresh desktop installation works.

## Working in a fork

Keep changes focused on a specific learning objective. `bun run test` runs frontend tests. `bun run validate` also checks frontend lint/types and backend lint/format/types/tests. These checks do not validate a packaged application's first run or current Gemini API access.

Use disposable application data for backend tests. Some tests exercise settings persistence and reset behavior, and the shared fixtures do not isolate every global application path. Redirect configuration/data paths before importing the application; the October 2026 review also redirected `platformdirs.user_data_dir` and blocked external connections. Running the suite unchanged against an existing user profile is not equivalent to that isolated review.

For a revived fork, verify packaging resources, model availability, streaming boundaries and multi-turn context before expanding features. Preserve a clear distinction between offline tests, live-model checks and desktop smoke tests.

The [Code of Conduct](CODE_OF_CONDUCT.md) remains available for interactions associated with this repository.
