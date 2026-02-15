# Pre-Commit Checklist for Backend

**IMPORTANT**: Always run these checks before committing any backend changes!

## Required Checks

Run all three checks from the `backend/` directory:

```bash
cd backend

# 1. Lint check (must pass)
uv run ruff check .

# 2. Format check (must pass)
uv run ruff format --check .

# 3. Unit tests (must pass)
uv run pytest tests/unit/ -v
```

## What to Do If Checks Fail

### Lint Errors
```bash
# Auto-fix many issues
uv run ruff check --fix .

# Check again
uv run ruff check .
```

### Format Errors
```bash
# Auto-format code
uv run ruff format .

# Check again
uv run ruff format --check .
```

### Test Failures
- Fix the failing tests
- Run again: `uv run pytest tests/unit/ -v`
- Make sure all tests pass before committing

## Integration Tests

Integration tests require PostgreSQL and will fail locally. They will pass in CI:

```bash
# These will error locally (expected)
uv run pytest tests/integration/ -v

# They pass in CI where PostgreSQL service is available
```

## Quick One-Liner

Run all checks at once:

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest tests/unit/ -v
```

If all three pass, you're good to commit! ✅

## Why This Matters

- **CI blocks merging** if lint or tests fail
- **Catching issues early** saves time and frustration
- **Local verification** is faster than waiting for CI
- **Clean commits** maintain code quality

## Optional: Git Pre-Commit Hook

Create `.git/hooks/pre-commit` to automatically run checks:

```bash
#!/bin/bash
cd backend
echo "Running pre-commit checks..."
uv run ruff check . || exit 1
uv run ruff format --check . || exit 1
uv run pytest tests/unit/ -q || exit 1
echo "All checks passed! ✅"
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

Now checks run automatically before every commit!
