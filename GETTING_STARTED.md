# Lab2FHIR - Getting Started

This guide will help you set up and run the Lab PDF to FHIR Converter.

## Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Node.js 20+ (for frontend)
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager

## Quick Start

### 1. Install uv (if not already installed)

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### 2. Set Up Database

```bash
# Create PostgreSQL database
createdb lab2fhir

# For testing
createdb lab2fhir_test
```

### 3. Install Backend Dependencies

```bash
cd backend
uv sync --all-extras
```

This will install all dependencies (including dev dependencies) and create a virtual environment automatically.

### 4. Configure Environment

```bash
cd backend
cp .env.example .env
# Edit .env with your database URL and other settings
```

### 5. Run Database Migrations

```bash
cd backend
uv run alembic upgrade head
```

### 6. Generate Test Fixtures

```bash
cd backend
uv run python tests/fixtures/generate_fixtures.py
```

### 7. Run the API Server

```bash
cd backend
uv run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### 7. Run the Frontend (Optional)

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Frontend UI: `http://localhost:5173` (if running separately)

## Testing

### Run All Tests

```bash
cd backend
uv run pytest
```

### Run Specific Test Types

```bash
# Unit tests only
uv run pytest tests/unit -v

# Integration tests only
uv run pytest tests/integration -v

# With coverage
uv run pytest --cov=src --cov-report=html
```

### Linting and Formatting

```bash
cd backend

# Check code with ruff
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Check formatting
uv run ruff format --check .

# Format code
uv run ruff format .
```

## Example Usage

### 1. Create a Patient

```bash
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "external_subject_id": "patient-001",
    "display_name": "John Doe",
    "subject_type": "human"
  }'
```

### 2. Upload a Lab Report PDF

```bash
curl -X POST http://localhost:8000/api/v1/reports \
  -F "patient_id=<PATIENT_ID>" \
  -F "file=@/path/to/lab_report.pdf"
```

### 3. Check Report Status

```bash
curl http://localhost:8000/api/v1/reports/<REPORT_ID>
```

### 4. View Parsed Data

```bash
curl http://localhost:8000/api/v1/parsed-data/<REPORT_ID>
```

### 5. Generate FHIR Bundle

```bash
curl -X POST http://localhost:8000/api/v1/bundles/<REPORT_ID>/generate
```

### 6. Download FHIR Bundle

```bash
curl http://localhost:8000/api/v1/bundles/<REPORT_ID>/download \
  -o bundle.json
```

## Project Structure

```
backend/
├── src/
│   ├── api/              # API endpoints (routers)
│   │   ├── patients.py   # Patient management
│   │   ├── reports.py    # Report upload and status
│   │   ├── parsed_data.py # Parsed data retrieval
│   │   ├── bundles.py    # FHIR bundle generation
│   │   └── errors.py     # Error handling
│   ├── db/
│   │   ├── models/       # SQLAlchemy ORM models
│   │   └── session.py    # Database session management
│   ├── domain/           # Business logic
│   │   ├── intermediate_schema.py  # Pydantic models
│   │   ├── report_state_machine.py # State transitions
│   │   ├── determinism.py          # ID generation
│   │   └── fhir_mapping.py         # FHIR helpers
│   ├── services/         # Service layer
│   │   ├── pdf_extraction_service.py
│   │   ├── parser_service.py
│   │   ├── report_pipeline_service.py
│   │   ├── fhir_bundle_service.py
│   │   └── storage_service.py
│   ├── config.py         # Application settings
│   └── main.py           # FastAPI app
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── contract/         # API contract tests
│   └── fixtures/         # Test data
├── alembic/              # Database migrations
└── pyproject.toml        # Project configuration
```

## Key Features

- ✅ **PDF Upload**: Upload text-based lab report PDFs
- ✅ **Duplicate Detection**: SHA-256 hash-based deduplication
- ✅ **Text Extraction**: Automatic text extraction with scanned-PDF rejection
- ✅ **Parsing**: Convert PDF text to intermediate JSON schema
- ✅ **FHIR Generation**: Create FHIR R4 transaction bundles
- ✅ **State Machine**: Enforced workflow transitions
- ✅ **Deterministic IDs**: Stable resource identifiers
- ✅ **LOINC Mapping**: Common analytes mapped to LOINC codes

## Troubleshooting

### Database Connection Issues

Make sure PostgreSQL is running and the DATABASE_URL in `.env` is correct:

```bash
# Test connection
psql -d lab2fhir -c "SELECT 1"
```

### Import Errors

Make sure you've installed the package in editable mode:

```bash
cd backend
pip install -e ".[dev]"
```

### Storage Directory Errors

The application will create storage directories automatically, but ensure the parent directories exist and are writable.

## Next Steps

1. Review the API documentation at `/docs`
2. Try the example workflow with a test PDF
3. Explore the FHIR bundle structure
4. Consider integrating with your FHIR server (e.g., Fasten, HAPI FHIR)

## Production Considerations

Before deploying to production:

1. **LLM Integration**: Replace the parser stub with a real LLM integration
2. **Authentication**: Add authentication and authorization
3. **Rate Limiting**: Add rate limiting for API endpoints
4. **Background Jobs**: Use a task queue (Celery, Dramatiq) for async processing
5. **Object Storage**: Replace filesystem storage with S3/Azure Blob
6. **Monitoring**: Add logging, metrics, and error tracking
7. **SSL/TLS**: Enable HTTPS for all connections
8. **Database Backups**: Set up automated backups
9. **Secrets Management**: Use a secrets manager for sensitive configuration

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

See [LICENSE](../LICENSE) for details.
