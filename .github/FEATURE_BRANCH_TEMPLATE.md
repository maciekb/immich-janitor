# Feature Branch Template

Quick reference for developing new features using proper Git workflow.

## Before You Start

1. ✅ Ensure you're on latest main: `git checkout main && git pull`
2. ✅ Check no uncommitted changes: `git status`
3. ✅ Decide on feature name (lowercase, hyphens, descriptive)

## Step-by-Step Workflow

### 1. Create Feature Branch

```bash
# Feature branch naming conventions:
# feature/name-of-feature  - New functionality
# fix/name-of-bug         - Bug fixes
# docs/name-of-change     - Documentation changes
# refactor/name-of-area   - Code refactoring

git checkout -b feature/your-feature-name
```

**Examples:**
- `feature/album-management`
- `feature/favorites-filter`
- `fix/pagination-timeout`
- `docs/api-reference`

### 2. Develop Your Feature

Make logical, atomic commits:

```bash
# Make changes
# Test locally: uv run pytest
# Test CLI: uv run immich-janitor your-command

git add <files>
git commit -m "feat: Add XYZ functionality"
```

**Good commit messages:**
```bash
git commit -m "feat: Add Album model and validation"
git commit -m "feat: Implement album CLI commands"
git commit -m "test: Add album management tests"
git commit -m "docs: Document album commands in README"
```

### 3. Keep Branch Updated

Regularly sync with main to avoid conflicts:

```bash
git fetch origin
git rebase origin/main

# If conflicts occur:
# 1. Resolve conflicts in files
# 2. git add <resolved-files>
# 3. git rebase --continue
```

### 4. Test Everything

Before pushing:

```bash
# Run tests
uv run pytest

# Test CLI manually
uv run immich-janitor --help
uv run immich-janitor your-new-command

# Check code style
# (add linter if configured)
```

### 5. Push and Create PR

```bash
# Push your branch
git push origin feature/your-feature-name

# Create PR using GitHub CLI (recommended)
gh pr create --title "feat: Add album management" \
             --body "$(cat <<EOF
## What
Adds album management functionality with list, create, and manage commands.

## Why
Users need to organize their assets into albums via CLI.

## How
- Added Album model with Pydantic validation
- Implemented album client methods (list, create, add_assets)
- Created CLI commands under 'albums' group
- Added comprehensive tests

## Testing
- [x] Unit tests added and passing
- [x] Manual testing performed with real Immich server
- [x] Documentation updated (README, EXAMPLES)

## Related Issues
Closes #123
EOF
)"

# Or interactively (will prompt for title/body)
gh pr create

# Or create via GitHub web interface
# Go to: https://github.com/your-username/immich-janitor
```

**GitHub CLI installation:**
```bash
# macOS
brew install gh

# Login
gh auth login

# Check PR status
gh pr status

# View PR in browser
gh pr view --web
```

### 6. After Merge

Clean up your local branch:

```bash
git checkout main
git pull
git branch -d feature/your-feature-name
```

## Feature Checklist

Before creating PR, ensure:

- [ ] Code compiles and runs
- [ ] Tests added and passing
- [ ] Documentation updated (README, EXAMPLES)
- [ ] No debug/console.log statements
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] Feature is complete (not WIP)

## When NOT to Use Feature Branch

Direct commits to main are OK for:

- Typo fixes
- Small doc updates
- Version bumps
- Hotfixes (but create issue first)
- Dependency updates

**Example:**
```bash
git checkout main
git commit -m "docs: Fix typo in README"
git push origin main
```

## PR Description Template

```markdown
## What

Brief description of the feature

## Why

Why is this needed? What problem does it solve?

## How

How was it implemented? Any important decisions?

## Testing

- [ ] Unit tests added
- [ ] Manual testing performed
- [ ] Documentation updated

## Screenshots (if applicable)

```

## Example: Adding Album Management

```bash
# 1. Create branch
git checkout -b feature/album-management

# 2. Implement step by step
git commit -m "feat: Add Album model"
git commit -m "feat: Add album client methods"
git commit -m "feat: Add album CLI commands"
git commit -m "test: Add album tests"
git commit -m "docs: Document album commands"

# 3. Keep updated
git fetch origin
git rebase origin/main

# 4. Test
uv run pytest
uv run immich-janitor albums list

# 5. Push and create PR with gh CLI
git push origin feature/album-management
gh pr create --title "feat: Add album management" \
             --body "Implements album list, create, and manage commands" \
             --label "enhancement"

# 6. Check PR status
gh pr status

# 7. View in browser if needed
gh pr view --web

# 8. After merge (can be done via gh too!)
gh pr merge --squash  # or via GitHub web UI
git checkout main
git pull
git branch -d feature/album-management
```

## GitHub CLI Workflow Tips

```bash
# Create draft PR (for WIP)
gh pr create --draft

# Convert draft to ready
gh pr ready

# Add reviewers
gh pr edit --add-reviewer username

# Add labels
gh pr edit --add-label "bug" --add-label "high-priority"

# Check if PR is ready to merge
gh pr checks

# Auto-merge after CI passes
gh pr merge --auto --squash
```

## Codex Bot Review Process

After creating a PR, **Codex bot** will automatically review your code:

### 1. **Automatic Review**
- Codex analyzes code quality automatically
- Wait for Codex to complete review (usually few minutes)

### 2. **If Codex Approves** 👍
- You'll see a thumbs up (👍) from Codex
- Code quality is good - ready to merge!
- Proceed with merge after any human reviews

### 3. **If Codex Has Concerns** 💬
- Codex will create a comment with specific issues
- Read the comment carefully - it contains:
  - Code quality issues
  - Suggestions for improvement
  - Specific lines/files to fix

### 4. **Fix Issues**
```bash
# Address Codex's concerns in your branch
git checkout feature/your-feature-name

# Make fixes based on Codex comments
# ... edit files ...

git add .
git commit -m "fix: Address Codex review comments"
git push origin feature/your-feature-name
```

### 5. **Request Re-review**
```bash
# Via GitHub CLI
gh pr comment --body "@codex review"

# Or via web UI:
# 1. Go to PR
# 2. Add new comment with: @codex review
# 3. Submit
```

### 6. **Iterate Until Approval**
- Codex will review again
- Repeat steps 4-5 until Codex gives 👍
- Then merge!

### Example Workflow with Codex:

```bash
# 1. Create PR
gh pr create --title "feat: Add album management"

# 2. Wait for Codex review...
# (Codex comments: "Consider adding error handling in line 45")

# 3. Fix issues
git checkout feature/album-management
# ... fix issues ...
git commit -m "fix: Add error handling as suggested by Codex"
git push

# 4. Request re-review
gh pr comment --body "@codex review"

# 5. Wait for Codex...
# (Codex gives 👍)

# 6. Merge!
gh pr merge --squash
```

### Tips for Working with Codex:

- ✅ **Read comments carefully** - Codex provides specific feedback
- ✅ **Fix all mentioned issues** - Don't skip any concerns
- ✅ **Use clear commit messages** - Help reviewers understand fixes
- ✅ **Request re-review** - Always use `@codex review` after fixes
- ✅ **Be patient** - Automated reviews may take a few minutes
- ❌ **Don't merge without approval** - Wait for Codex 👍

## Questions?

See CONTRIBUTING.md for full guidelines.
