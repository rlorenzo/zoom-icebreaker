# Contributing to Icebreaker Tracker

Thank you for considering contributing to the Icebreaker Tracker!

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/zoom-icebreaker.git
    cd zoom-icebreaker
    ```

2. **Install dependencies and set up pre-commit**:

    ```bash
    uv sync --dev
    npm ci   # only needed if you touch index.html, the JS, or styles.css
    uv run pre-commit install --hook-type pre-commit --hook-type pre-push
    ```

    Installing the pre-push hook too is what enables the slower gates
    (`pip-audit`, `fallow`, `vitest`), which are staged on push rather than on
    every commit.

## Workflow

1. **Create a branch** for your change.
2. **Make your changes**.
3. **Run checks locally** before committing:

    ```bash
    uv run pre-commit run --all   # commit-stage hooks, pytest included
    npm test                      # web suite (vitest), if you touched the web assets
    ```

    `pre-commit run --all` covers `ruff` (lint + format), `mypy` (strict),
    `bandit` and `gitleaks` (security), `lizard` (complexity), `pylint`
    (duplicate code), `pytest`, `pymarkdown`, `biome`, and `html-validate`.
    See the [README's Development section](README.md#development) for the full
    tool list and what runs on push versus on commit.
4. **Submit a Pull Request**.

## Guidelines

- **Code Quality**: Ensure your code follows the existing style (checked by `ruff`).
- **Documentation**: Update `README.md` or `DESIGN.md` if your change adds or alters functionality.
- **Accessibility**: This project prioritizes accessibility (keyboard navigation, ARIA, reduced motion). Ensure your changes do not degrade the experience for users with assistive technologies.
- **Small PRs**: Favor small, focused PRs over large ones.

## Reporting Issues

Use the GitHub Issue tracker to report bugs or suggest features. Please provide as much detail as possible, including steps to reproduce the issue.
