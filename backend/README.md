# Lab2FHIR Backend

Backend API for Lab PDF to FHIR Converter.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable dependency management.

```bash
# Install uv (if not already installed)
pip install uv

# Install dependencies (creates virtual environment automatically)
uv sync --all-extras

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Start development server
uv run uvicorn src.main:app --reload
```

## Dependencies

Dependencies are managed in `pyproject.toml` and locked in `uv.lock`:

```bash
# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Update dependencies
uv lock --upgrade

# Sync environment with lock file
uv sync
```

## Structure

- `src/` - Application source code
  - `api/` - FastAPI routers and endpoints
  - `domain/` - Business logic, schemas, state machines
  - `services/` - External integrations and orchestration
  - `db/` - Database models and migrations
- `tests/` - Test suite
  - `unit/` - Unit tests
  - `integration/` - Integration tests
  - `contract/` - API contract tests
  - `fixtures/` - Test data and synthetic PDFs
