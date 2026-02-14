# Lab2FHIR Python Project Structure

This document outlines the recommended Python project structure for Lab2FHIR.

## Directory Structure

```
Lab2FHIR/
├── .devcontainer/
│   └── devcontainer.json          # GitHub Codespaces configuration
├── .github/
│   ├── workflows/
│   │   ├── tests.yml              # Test automation
│   │   ├── lint.yml               # Linting automation
│   │   └── deploy.yml             # Deployment automation (future)
│   └── dependabot.yml             # Automated dependency updates
├── docs/
│   ├── planning/                  # Project planning documents
│   ├── architecture.md            # System architecture
│   ├── api.md                     # API documentation
│   └── deployment.md              # Deployment guide
├── src/
│   └── lab2fhir/
│       ├── __init__.py
│       ├── api/                   # Web API (Flask/FastAPI)
│       │   ├── __init__.py
│       │   ├── app.py             # Application factory
│       │   ├── routes.py          # API endpoints
│       │   └── schemas.py         # Request/response schemas
│       ├── ingestion/             # PDF ingestion layer
│       │   ├── __init__.py
│       │   ├── storage.py         # File storage
│       │   ├── deduplication.py   # Hash-based deduplication
│       │   └── validation.py      # File validation
│       ├── parsing/               # LLM parsing layer
│       │   ├── __init__.py
│       │   ├── extractor.py       # PDF text extraction
│       │   ├── llm.py             # OpenAI integration
│       │   ├── schema.py          # Pydantic models
│       │   └── prompts.py         # LLM prompt templates
│       ├── normalization/         # Data normalization
│       │   ├── __init__.py
│       │   ├── units.py           # Unit conversion
│       │   ├── dates.py           # Date parsing
│       │   ├── values.py          # Value validation
│       │   └── analytes.py        # Analyte name mapping
│       ├── fhir/                  # FHIR generation
│       │   ├── __init__.py
│       │   ├── builders.py        # FHIR resource builders
│       │   ├── observation.py     # Observation resources
│       │   ├── diagnostic_report.py  # DiagnosticReport resources
│       │   ├── document_reference.py # DocumentReference resources
│       │   ├── bundle.py          # Bundle creation
│       │   └── validation.py      # FHIR validation
│       ├── integration/           # FHIR server integration
│       │   ├── __init__.py
│       │   ├── client.py          # FHIR HTTP client
│       │   ├── submission.py      # Bundle submission
│       │   └── retry.py           # Retry logic
│       ├── models/                # Database models
│       │   ├── __init__.py
│       │   ├── document.py        # Document model
│       │   ├── patient.py         # Patient/subject model
│       │   └── parse_result.py    # Parse result model
│       ├── db.py                  # Database connection
│       ├── config.py              # Configuration management
│       └── cli.py                 # CLI interface (future)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── fixtures/
│   │   └── sample_lab.pdf         # Test PDFs
│   ├── unit/                      # Unit tests
│   │   ├── test_ingestion.py
│   │   ├── test_parsing.py
│   │   ├── test_normalization.py
│   │   └── test_fhir.py
│   └── integration/               # Integration tests
│       ├── test_api.py
│       └── test_end_to_end.py
├── migrations/                    # Alembic database migrations
│   ├── env.py
│   └── versions/
├── .gitignore
├── .pre-commit-config.yaml        # Pre-commit hooks
├── pyproject.toml                 # Project configuration
├── poetry.lock                    # Locked dependencies
├── Makefile                       # Common commands
├── README.md                      # Project overview
├── CONTRIBUTING.md                # Contribution guide
└── Procfile                       # Heroku deployment (future)
```

## Technology Stack

### Core Dependencies
- **Python**: 3.11+ (use 3.12 for latest features)
- **Web Framework**: FastAPI (async, auto-docs) or Flask (simpler)
- **Database ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 15+
- **Migrations**: Alembic
- **FHIR Library**: fhir.resources
- **PDF Parsing**: pdfplumber or pypdf
- **LLM**: OpenAI Python SDK
- **Validation**: Pydantic 2.x
- **HTTP Client**: httpx (async) or requests

### Development Dependencies
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Linting**: ruff (fast, replaces flake8/black/isort)
- **Type Checking**: mypy
- **Pre-commit**: pre-commit
- **Mocking**: pytest-mock
- **Fixtures**: factory_boy or faker

### Deployment Dependencies (Future)
- **WSGI Server**: gunicorn (for Flask) or uvicorn (for FastAPI)
- **Process Management**: honcho (Heroku-style)
- **Environment**: python-dotenv
- **Monitoring**: sentry-sdk (optional)

## pyproject.toml Template

```toml
[tool.poetry]
name = "lab2fhir"
version = "0.1.0"
description = "Convert laboratory PDF reports into FHIR resources"
authors = ["Ben Langfeld <ben@langfeld.me>"]
readme = "README.md"
packages = [{include = "lab2fhir", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = "^2.0.0"
alembic = "^1.13.0"
psycopg2-binary = "^2.9.9"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
fhir-resources = "^7.1.0"
openai = "^1.10.0"
pdfplumber = "^0.11.0"
python-multipart = "^0.0.6"
httpx = "^0.26.0"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
pytest-asyncio = "^0.23.0"
pytest-mock = "^3.12.0"
ruff = "^0.1.0"
mypy = "^1.8.0"
pre-commit = "^3.6.0"
factory-boy = "^3.3.0"
faker = "^22.0.0"

[tool.poetry.scripts]
lab2fhir = "lab2fhir.cli:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.ruff]
line-length = 100
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=lab2fhir",
    "--cov-report=term-missing",
    "--cov-report=html",
]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

## Makefile Template

```makefile
.PHONY: help install test lint format clean run migrate

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linters"
	@echo "  make format    - Format code"
	@echo "  make clean     - Clean cache files"
	@echo "  make run       - Run development server"
	@echo "  make migrate   - Run database migrations"

install:
	poetry install

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=lab2fhir --cov-report=html

lint:
	poetry run ruff check .
	poetry run mypy src/

format:
	poetry run ruff format .
	poetry run ruff check --fix .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov coverage.xml .coverage

run:
	poetry run uvicorn lab2fhir.api.app:app --reload

migrate:
	poetry run alembic upgrade head

migrate-create:
	poetry run alembic revision --autogenerate -m "$(msg)"
```

## .gitignore Template

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json
.pyre/
.pytype/

# Linting
.ruff_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
*.env

# Database
*.db
*.sqlite3
*.sql

# Logs
*.log
logs/

# Uploads (development)
uploads/
temp/

# Poetry
poetry.lock  # Commit this for applications, ignore for libraries
```

## Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]
```

## Getting Started

1. **Initialize project**:
   ```bash
   poetry init
   # Or copy the pyproject.toml template above
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Set up pre-commit**:
   ```bash
   poetry run pre-commit install
   ```

4. **Create basic structure**:
   ```bash
   mkdir -p src/lab2fhir/{api,ingestion,parsing,normalization,fhir,integration,models}
   mkdir -p tests/{unit,integration,fixtures}
   touch src/lab2fhir/__init__.py
   # Create __init__.py in all subdirectories
   ```

5. **Start coding**! Begin with the MVP tasks.
