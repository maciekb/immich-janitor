# AI Agent Guidelines for Immich Janitor

This document provides essential, static context for AI agents (like Goose, Cursor, Copilot) working on this project.

## 🚨 CRITICAL: Pre-Flight Checklist

**BEFORE starting ANY work:**

### 1. Check Current Branch
```bash
git branch --show-current
```

### 2. Decision: Branch or Direct?

**If on `main`, determine if branch is needed:**

#### ✅ Direct to Main (No Branch) - ONLY These 3 Cases:

1. **Single typo fix**
   - Example: `"teh" → "the"`, `"functino" → "function"`
   - Only 1-3 characters changed
   - In comments, docs, or strings

2. **Version bump only**
   - Example: `version = "0.3.0" → "0.3.1"` in `pyproject.toml`
   - ONLY the version field, nothing else

3. **Critical hotfix**
   - Production system is broken/unusable
   - Users cannot use the tool
   - Must be fixed immediately

#### ⚠️ Everything Else → Create Feature Branch:

```bash
git checkout -b feature/descriptive-name
# or fix/*, docs/*, refactor/*
```

**This includes:**
- Any code changes (even "small" ones)
- Documentation updates (even single paragraph)
- Multiple file edits
- New features or commands
- Bug fixes
- Refactoring
- **If you're unsure: CREATE BRANCH**

### 3. If You Started on Main by Mistake

**Realized mid-work this should be on branch?**

```bash
# STOP before committing
# Save your work
git stash

# Create proper branch
git checkout -b feature/what-you-were-doing

# Restore work
git stash pop

# Continue normally
```

**Better to fix this now than commit to main and revert later.**

---

**Rule of thumb: When in doubt, create a branch. It's always safer.**

See [DEVELOPER_GUIDELINES.md](.github/DEVELOPER_GUIDELINES.md) for complete workflow.

---

## Project Overview

**Immich Janitor** is a CLI tool for managing Immich photo library via API.

- **Language:** Python 3.12+
- **Package Manager:** uv
- **Framework:** Click (CLI), Pydantic (models), httpx (HTTP), Rich (terminal UI)
- **Testing:** pytest

### Architecture

```
CLI Layer (Click)
    ↓
Client Layer (httpx + API wrapper)
    ↓
Data Models (Pydantic)
    ↓
Immich API (REST)
```

---

## Project Structure

```
immich-janitor/
├── immich_janitor/          # Main package
│   ├── cli.py              # Main CLI entry point
│   ├── cli_*.py            # Command group modules
│   ├── client.py           # Immich API client
│   ├── models.py           # Pydantic data models
│   ├── config.py           # Configuration loading
│   └── utils.py            # Utility functions
├── tests/                   # Test suite
│   └── test_*.py           # Test modules
├── .github/                 # Workflows and templates
│   ├── DEVELOPER_GUIDELINES.md
│   ├── PR_WORKFLOW.md
│   └── FEATURE_BRANCH_WORKFLOW.md
├── README.md               # User documentation
├── CONTRIBUTING.md         # Contributor guide
└── pyproject.toml          # Project metadata
```

---

## Key Technical Context

### API Client Patterns

**Immich API Interaction:**
- Uses REST API with JSON payloads
- Pagination: 1000 items per page maximum
  - ⚠️ **Critical pattern:** Continue fetching until `len(items) < page_size`
  - ⚠️ **Don't trust `total` field** in API responses for pagination logic
- EXIF data: Must be explicitly requested via parameters
- All API calls go through centralized client wrapper

**Why this matters:**
- Pagination bug is a common mistake (stopping at first page)
- EXIF data (like file sizes) requires specific request parameters
- Client wrapper handles authentication, error handling, retries

### Data Model Patterns

**Pydantic Models:**
- All API responses mapped to Pydantic models
- Use `Field(alias="...")` for API field name mapping
- Optional fields handle incomplete API responses
- Properties provide convenient access to nested data

**Common pattern:**
```python
class OuterModel(BaseModel):
    nested: Optional[InnerModel] = Field(None, alias="apiName")
    
    @property
    def convenient_access(self):
        return self.nested.value if self.nested else None
```

### CLI Command Patterns

**Standard CLI Command Structure:**
```python
@command_group.command()
@click.option("--dry-run", is_flag=True, help="Preview only")
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_context
def command_name(ctx, dry_run: bool, force: bool):
    """Command description."""
    client = ctx.obj["client"]
    
    # Fetch data
    with console.status("Loading..."):
        data = client.fetch_data()
    
    # Show what will happen
    display_preview(data)
    
    if dry_run:
        return
    
    # Confirm
    if not force:
        if not click.confirm("Continue?"):
            return
    
    # Execute
    client.perform_action(data)
```

**Destructive operations must have:**
- `--dry-run` flag for preview
- `--force` flag to skip confirmation
- Clear preview of what will happen
- Confirmation prompt by default

---

## Common Development Patterns

### Adding New CLI Command

1. Determine appropriate command group or create new one
2. Use Click decorators for arguments and options
3. Access client via `@click.pass_context`
4. Follow destructive operation patterns (dry-run, force, confirmation)
5. Use Rich library for all terminal output
6. Write tests with mocked API calls
7. Update README.md with examples

### Working with API

```python
# Fetch data with proper error handling
try:
    data = client.fetch_data()
except httpx.HTTPError as e:
    console.print(f"[red]Error: {e}[/red]")
    raise click.Abort()

# Always paginate properly
all_items = []
page = 1
while True:
    response = fetch_page(page)
    items = response.get("items", [])
    if not items:
        break
    all_items.extend(items)
    if len(items) < page_size:  # Last page
        break
    page += 1
```

### Writing Tests

```python
# Use fixtures for test data
@pytest.fixture
def sample_data():
    return [Model(...), Model(...)]

# Mock external dependencies
with patch.object(client, '_make_request') as mock:
    mock.return_value = Mock(json=lambda: {"items": [...]})
    result = client.fetch_data()
    assert len(result) > 0

# Test edge cases
def test_empty_response():
    # What happens when API returns nothing?
    
def test_pagination_multiple_pages():
    # Regression test: ensure pagination works
    
def test_error_handling():
    # What happens when API errors?
```

---

## Known Patterns & Anti-Patterns

### ✅ Good Patterns

- Paginate until no more items, not based on `total` field
- Request EXIF data explicitly when needed
- Use Rich for all terminal output
- Mock all external calls in tests
- Add regression tests for every bug fixed
- Use type hints everywhere
- Clear, descriptive error messages

### ❌ Anti-Patterns to Avoid

- Trusting API `total` field for pagination
- Assuming data always present (use Optional)
- Hitting real API in tests
- print() instead of Rich console
- Committing directly to main branch
- Missing tests for new features
- Vague error messages

---

## Documentation Structure

This project uses multiple documentation files:

- **AGENTS.md** (this file) - Static context for AI agents
- **[README.md](README.md)** - User-facing features and usage examples
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributor guide and workflow basics
- **[.github/DEVELOPER_GUIDELINES.md](.github/DEVELOPER_GUIDELINES.md)** - Complete development workflow
- **[.github/PR_WORKFLOW.md](.github/PR_WORKFLOW.md)** - Pull request process details
- **[.github/FEATURE_BRANCH_WORKFLOW.md](.github/FEATURE_BRANCH_WORKFLOW.md)** - Git branching strategy

**For current features, active issues, version history, or step-by-step procedures, see the documents above.**

---

## Testing Philosophy

- **Unit tests:** Mock external dependencies
- **Fast tests:** No network calls, no file I/O in unit tests
- **Regression tests:** Every bug gets a test
- **Coverage:** Aim for >80% on new code
- **Descriptive names:** Test name explains what's tested
- **Test structure:** Arrange, Act, Assert

---

## Code Style Guidelines

- **Type hints:** Required for all function signatures
- **Docstrings:** Required for public functions and classes
- **Imports:** Organize as: stdlib, third-party, local
- **Naming:** snake_case for functions/variables, PascalCase for classes
- **Error handling:** Explicit messages, graceful failures
- **Rich output:** Use Rich library, not print()

---

## External Resources

- **Immich API:** https://api.immich.app/
- **Immich GitHub:** https://github.com/immich-app/immich
- **Click docs:** https://click.palletsprojects.com/
- **Rich docs:** https://rich.readthedocs.io/
- **Pydantic docs:** https://docs.pydantic.dev/
- **pytest docs:** https://docs.pytest.org/

---

## For AI Agents: Core Principles

When working on this codebase, remember:

1. **Always check branch first** - Prevents accidental commits to main
2. **Follow existing patterns** - Look at similar code for consistency  
3. **Test everything** - Features need tests, bugs need regression tests
4. **Update appropriate docs** - User changes → README, workflow → guidelines
5. **Type hints required** - They're mandatory and helpful
6. **Mock external calls** - Tests must be fast and isolated
7. **Rich for output** - It's the project standard for terminal UI
8. **Pagination pattern** - Continue until items < page_size, don't trust total
9. **Destructive operations** - Need dry-run, force flags, and confirmation

**This file is intentionally static.** For feature-specific details, current state, or evolving processes, consult the documentation structure above.
