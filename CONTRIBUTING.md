# Contributing to Immich Janitor

Thank you for your interest in contributing to Immich Janitor! 🎉

## Development Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/immich-janitor.git
   cd immich-janitor
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Set up your environment**:
   Copy `.env.example` to `.env` and add your Immich API credentials.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=immich_janitor

# Run specific test file
uv run pytest tests/test_models.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused and small

## Making Changes

1. **Create a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and add tests

3. **Run tests** to ensure everything works:
   ```bash
   uv run pytest
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**

## Adding New Features

When adding new features:

1. Update the relevant code
2. Add tests for the new functionality
3. Update the README.md if needed
4. Add the feature to the roadmap checklist

## Reporting Bugs

When reporting bugs, please include:

- Your Immich version
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any error messages or logs

## Feature Requests

Feature requests are welcome! Please:

- Check if the feature has already been requested
- Clearly describe the feature and its use case
- Explain why it would be useful to most users

## Code of Conduct

Be respectful and constructive in all interactions.

## Questions?

If you have questions, feel free to open an issue for discussion.

Thank you for contributing! 🙏
