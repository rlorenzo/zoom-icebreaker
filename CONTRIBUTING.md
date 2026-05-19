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
    uv run pre-commit install
    ```

## Workflow

1. **Create a branch** for your change.
2. **Make your changes**.
3. **Run checks locally** before committing:

    ```bash
    uv run pre-commit run --all
    ```

    This runs `ruff` (linting/formatting), `bandit` (security), `lizard` (complexity), and `pymarkdown` checks.
4. **Submit a Pull Request**.

## Guidelines

- **Code Quality**: Ensure your code follows the existing style (checked by `ruff`).
- **Documentation**: Update `README.md` or `DESIGN.md` if your change adds or alters functionality.
- **Accessibility**: This project prioritizes accessibility (keyboard navigation, ARIA, reduced motion). Ensure your changes do not degrade the experience for users with assistive technologies.
- **Small PRs**: Favor small, focused PRs over large ones.

## Reporting Issues

Use the GitHub Issue tracker to report bugs or suggest features. Please provide as much detail as possible, including steps to reproduce the issue.
