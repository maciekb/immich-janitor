# Developer Guidelines

## 🚨 CRITICAL: Git Workflow Pre-Flight Checklist

**MANDATORY before starting ANY new feature, fix, or refactoring:**

### Pre-Work Checklist:

1. **Check current branch**
   ```bash
   git branch --show-current
   ```

2. **If on `main` or `master`**: **STOP! Create feature branch first**
   ```bash
   # DO NOT write code on main!
   git checkout -b feature/descriptive-name
   ```

3. **Branch naming conventions**:
   - `feature/descriptive-name` - New features
   - `fix/issue-description` - Bug fixes  
   - `docs/what-changed` - Documentation updates
   - `refactor/component-name` - Code refactoring
   - `test/what-testing` - Test additions/updates

4. **Only THEN start coding**

### Why This Matters:

- ✅ Keeps main branch clean and deployable
- ✅ Enables proper code review through PRs
- ✅ Allows parallel work on multiple features
- ✅ Makes it easy to abandon/restart work
- ✅ Creates clear history of changes

### ⚠️ If You Already Started on Main:

```bash
# Save your work
git stash

# Create proper branch
git checkout -b feature/your-feature-name

# Restore your work
git stash pop

# Continue as normal
```

---

## Development Workflow

### 1. Starting New Work

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/new-feature

# Start coding...
```

### 2. During Development

```bash
# Commit regularly with conventional commits
git add .
git commit -m "feat: add new functionality"

# Push to origin
git push -u origin feature/new-feature
```

### 3. Before Creating PR

```bash
# Run tests
pytest --no-cov

# Check if main is ahead
git fetch origin main
git log HEAD..origin/main --oneline

# If main has changes, rebase (optional but recommended)
git rebase origin/main

# Push
git push origin feature/new-feature
```

### 4. Creating PR

```bash
# Using GitHub CLI (preferred)
gh pr create --title "feat: description" --body "..." --base main

# Or use GitHub UI
# https://github.com/your-repo/compare/main...feature/your-feature
```

### 5. After PR Merge

```bash
# Return to main
git checkout main

# Pull merged changes
git pull origin main

# Delete local feature branch
git branch -d feature/your-feature

# Delete remote feature branch (if not auto-deleted)
git push origin --delete feature/your-feature
```

---

## Conventional Commits

All commits MUST follow conventional commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Build/tooling changes
- `ci:` - CI/CD changes

### Examples:

```bash
git commit -m "feat: add interactive regex builder"
git commit -m "fix: properly fetch all assets with pagination"
git commit -m "docs: update README with new features"
git commit -m "test: add unit tests for regex helper"
```

---

## Code Quality Standards

### Before Committing:

1. **Run tests**
   ```bash
   pytest --no-cov -v
   ```

2. **Check code style** (if linter configured)
   ```bash
   ruff check .
   black --check .
   ```

3. **Verify no debug code**
   - Remove `print()` statements
   - Remove commented-out code
   - Remove `TODO` comments (or create issues)

### Writing Good Code:

- ✅ Write descriptive variable/function names
- ✅ Add docstrings to functions/classes
- ✅ Keep functions small and focused
- ✅ Add type hints
- ✅ Write tests for new functionality
- ✅ Update documentation

---

## Testing Guidelines

### Writing Tests:

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what's being tested

### Test Structure:

```python
def test_feature_does_expected_thing():
    """Test that feature behaves correctly in normal case."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

### Coverage:

- Aim for >80% coverage on new code
- Test happy paths AND edge cases
- Test error handling
- Use mocks for external dependencies (API calls, file I/O)

---

## Documentation Standards

### Update Documentation When:

- Adding new features
- Changing existing behavior
- Adding new CLI commands
- Adding new configuration options

### What to Update:

1. **README.md** - Main project documentation
2. **EXAMPLES.md** - Practical usage examples
3. **Docstrings** - In-code documentation
4. **CHANGELOG.md** - Version history (if exists)

### Writing Good Docs:

- ✅ Provide examples
- ✅ Explain WHY, not just WHAT
- ✅ Keep it up-to-date
- ✅ Use clear, simple language
- ✅ Include screenshots/output samples

---

## PR Review Checklist

### Before Requesting Review:

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Self-reviewed code
- [ ] No unnecessary changes (whitespace, formatting in unrelated files)
- [ ] Commit messages follow conventions
- [ ] Branch is up-to-date with main

### During Review:

- Be open to feedback
- Respond to all comments
- Make requested changes promptly
- Re-request review after changes

---

## Version Bumping

After merging significant features:

1. **Update version in `pyproject.toml`**
   ```toml
   version = "0.3.0"  # Follow semver
   ```

2. **Commit version bump**
   ```bash
   git commit -am "chore: bump version to 0.3.0"
   ```

3. **Create git tag**
   ```bash
   git tag -a v0.3.0 -m "Release v0.3.0: Interactive regex builder"
   ```

4. **Push with tags**
   ```bash
   git push origin main --tags
   ```

### Semantic Versioning:

- **MAJOR** (1.0.0) - Breaking changes
- **MINOR** (0.1.0) - New features (backwards compatible)
- **PATCH** (0.0.1) - Bug fixes

---

## Getting Help

- Check existing documentation first
- Look at similar code in the project
- Ask in discussions/issues
- Reference the workflow docs in `.github/`

---

## Remember:

**🚨 ALWAYS create a feature branch before starting work!**

This is the most important rule in this document.
