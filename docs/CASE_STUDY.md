# GeminiSensei: from a desktop tutor to a learning workflow

GeminiSensei was a competition project and a practical exercise in building a standalone AI application. I felt that a good AI education system was missing, and wanted to explore a tutor that could organize learning and guide a student through questions instead of only supplying answers.

The project is now complete as a learning exercise and retired from active development. Its value to me is the experience of connecting a product idea to a working codebase, understanding the integration costs, and reconsidering whether the product format matched my need.

## My contribution

I did most of the project work. A friend and AI helped with the UI. The most difficult areas for me were connecting the frontend and backend and working on project optimization.

The implementation spans a React interface, a Rust/Tauri desktop shell, a Python API, local persistence and model-backed workflows. Those boundaries made the project useful practice for my direction as a product-minded software engineer building backend and systems foundations, with an eventual focus on applied AI.

## Integration decisions and tradeoffs

Tauri provided a desktop shell while a Python sidecar gave me access to FastAPI and the AI tooling I was exploring. The shell starts the backend and passes its connection details to React; normal application requests then travel directly over local HTTP. This allowed the UI and Python services to stay separate, but introduced process startup, authentication, packaging and platform concerns. See the [architecture](ARCHITECTURE.md) for the actual flow.

LangGraph made teacher, reviewer and routing steps explicit. SQLAlchemy and Alembic handled structured application data, while separate SQLite checkpoints retained agent state. These were opportunities to learn orchestration and persistence, but they also created more moving parts to package and test.

Streaming was another boundary: a model's text chunks, server-sent events and browser network chunks are different units. The later review showed why treating them as interchangeable is a correctness problem, even when a simple example works.

## What the later review showed

A review on **18 October 2026** examined commit [`c2131c6`](https://github.com/lonlydwolf/GeminiSensei/commit/c2131c6e4852e934047d06a046b7c0dbabf7e2f6), rather than a newly repaired version. It found useful test coverage alongside gaps in the delivered experience:

- **Tests and release checks answer different questions.** All 104 backend tests passed in an isolated, offline run. The inspected macOS ARM64 release nevertheless omitted required migration resources and dynamically discovered agent modules. A clean packaged first-run check would have tested a different and necessary boundary.
- **API integration has a lifecycle.** The key-verification path uses a model that has since shut down. A valid credential can encounter an obsolete dependency before reaching the intended feature.
- **Small transport assumptions matter.** Direct tests of the frontend streaming method reproduced lost spaces, exposed event framing and dropped numeric text.
- **Persistence is not the same as useful model context.** Checkpoints store history, but the teacher's response-generation prompt uses only the latest user message plus lesson information.
- **Claims need evidence.** Search was not enabled in teacher generation, and prompt-based guardrails did not justify the original guarantees about hallucinations or learning progression.

These are review findings and lessons for future work, not fixes shipped in this closeout. The run used frozen Python dependencies, Python 3.14.8, temporary application data and blocked external connections. It did not test live Gemini access, educational outcomes or the full desktop application. The [README](../README.md#known-limitations) records the current limitations.

## Why I moved on

After building and experimenting with GeminiSensei, I concluded that a standalone application was not the best fit for my own learning need without a good workflow around it. That is a conclusion about my use case, not a claim that standalone educational software is inherently unsuitable.

I researched and experimented further, which led to [Faculty](https://github.com/lonlydwolf/skills/tree/main/skills/faculty): a skills-based learning workflow. Faculty continues that exploration with explicit roles for planning, teaching, evaluation and review.

For future applied-AI projects, I would start with a smaller workflow, test the complete user path early, and make claims only as strong as the evidence. GeminiSensei remains a record of the engineering work and product judgment that helped me reach that point.
