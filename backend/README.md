# Lab2FHIR Backend

Backend API for Lab PDF to FHIR Converter.

## Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Start development server
uvicorn src.main:app --reload
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
