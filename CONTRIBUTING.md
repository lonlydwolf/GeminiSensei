# Contributing to GeminiSensei

First off, thank you for considering contributing to GeminiSensei! Your help is greatly appreciated.

## Code of Conduct

This project and everyone participating in it is governed by a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior.

## How to Contribute

We welcome contributions in various forms, including bug reports, feature requests, documentation improvements, and code contributions.

### Reporting Bugs or Requesting Features

If you find a bug or have an idea for a new feature, please [open an issue](https://github.com/lonlydwolf/GeminiSensei/issues) on our GitHub repository. Provide as much detail as possible, including steps to reproduce the bug or a clear description of the feature.

### Contributing Code

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally.
3.  **Create a new branch** for your changes. We recommend using a descriptive branch name (e.g., `feat/add-new-feature` or `fix/resolve-issue-123`).
4.  **Set up the development environment**:
    ```bash
    bun install
    bun run sidecar:install
    ```
5.  **Make your changes**. Ensure you follow the development standards outlined below.
6.  **Test your changes**. Run the test suite to ensure everything is working correctly.
    ```bash
    bun run test
    ```
7.  **Commit your changes** following the commit message guidelines.
8.  **Push your changes** to your fork.
9.  **Open a pull request** to the `develop` branch of the main repository.

## Development Standards

*   **Version Control**: We use `jj` (Jujutsu) for development, but contributors are welcome to use `git`. Pull requests should be made to the `develop` branch.
*   **Commit Messages**: Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
    *   `feat`: for new features
    *   `fix`: for bug fixes
    *   `docs`: for documentation changes
    *   `chore`: for routine maintenance
    *   `refactor`: for code changes that neither fix a bug nor add a feature
*   **Code Style**:
    *   **Small Files**: Keep files focused and preferably under 800 lines.
    *   **Async First**: Use `async/await` for all I/O operations in both Python and TypeScript.
    *   **Type Safety**: Use Pydantic for data validation in Python and TypeScript interfaces for type safety in the frontend.
*   **AI Philosophy**: The AI assistant's primary role is to guide, not to provide direct answers. It should use Socratic questioning to encourage critical thinking.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.