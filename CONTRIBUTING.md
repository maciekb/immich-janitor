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

## Git Branching Strategy

We follow a simplified Git Flow approach to keep the codebase organized and stable.

### Branch Types

#### Feature Branches (`feature/*`)
**Use for:**
- New functionality (e.g., `feature/album-management`)
- Scope changes or significant refactoring
- Documentation framework changes
- Any change that takes multiple commits

**Workflow:**
```bash
# Create feature branch from main
git checkout main
git pull
git checkout -b feature/your-feature-name

# Work on your feature (multiple commits OK)
git add .
git commit -m "Add feature: description"

# Keep up to date with main
git fetch origin
git rebase origin/main

# Push and create PR
git push origin feature/your-feature-name
```

**Examples:**
- `feature/stats-commands` - Statistics functionality
- `feature/duplicate-detection` - Duplicate management
- `feature/trash-management` - Trash operations
- `feature/album-support` - Album management

#### Fix Branches (`fix/*`)
**Use for:**
- Bug fixes that require investigation
- Performance improvements
- API integration fixes

**Examples:**
- `fix/api-pagination` - Fix pagination bug
- `fix/memory-leak` - Fix memory leak issue

#### Docs Branches (`docs/*`)
**Use for:**
- Major documentation restructuring
- Switching documentation frameworks
- Multi-file documentation updates

**Examples:**
- `docs/api-reference` - Add complete API reference
- `docs/migrate-to-mkdocs` - Switch to MkDocs

### Direct to Main (No Branch)

**Use for:**
- Typo fixes in code or docs
- Small documentation updates after simple changes
- Hotfixes in production
- Version bumps
- Dependency updates

**Examples:**
```bash
# Fix typo
git commit -m "Fix typo in README"

# Update docs after small change
git commit -m "docs: Update CLI help text"

# Hotfix
git commit -m "hotfix: Fix critical API timeout issue"
```

### Commit Message Conventions

Use conventional commits for clarity:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat: Add duplicate detection commands"
git commit -m "fix: Correct pagination logic in API client"
git commit -m "docs: Update README with new commands"
git commit -m "chore: Bump version to 0.3.0"
```

### Pull Request Guidelines

1. **One feature per PR** - Keep PRs focused
2. **Update documentation** - Include README/EXAMPLES updates
3. **Add tests** - For new functionality
4. **Run tests** - Ensure all tests pass
5. **Keep commits clean** - Squash if needed
6. **Link issues** - Reference related issues

### Main Branch Protection

The `main` branch should always be:
- ✅ Stable and deployable
- ✅ Passing all tests
- ✅ Properly documented
- ✅ Tagged for releases

### When to Branch vs. Direct Commit

```
┌─────────────────────────────────────┬──────────────────────┐
│ Change Type                         │ Strategy             │
├─────────────────────────────────────┼──────────────────────┤
│ New command/feature                 │ Feature branch       │
│ Multiple related changes            │ Feature branch       │
│ Refactoring                         │ Feature branch       │
│ Doc framework change                │ Docs branch          │
│ Complex bug fix                     │ Fix branch           │
│                                     │                      │
│ Typo fix                           │ Direct to main       │
│ Small doc update                   │ Direct to main       │
│ Version bump                       │ Direct to main       │
│ Critical hotfix                    │ Direct to main       │
└─────────────────────────────────────┴──────────────────────┘
```

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
