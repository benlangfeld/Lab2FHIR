# Lab2FHIR Quickstart Guide

**Goal**: Get Lab2FHIR running locally in under 10 minutes

**What you'll build**: A self-hosted pipeline that converts lab PDF reports into FHIR R4-compliant resources (Observations, DiagnosticReports, DocumentReferences) for personal health record management.

---

## Prerequisites

### Required Software

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/) or use Docker
- **Git** - [Download](https://git-scm.com/downloads)

### Optional (for Docker deployment)

- **Docker & Docker Compose** - [Download](https://docs.docker.com/get-docker/)

### Required API Keys

- **OpenAI API Key** (or Anthropic/local LLM endpoint) - For PDF text parsing
  - Get key: https://platform.openai.com/api-keys
  - Recommended model: `gpt-4o` (best accuracy) or `gpt-4o-mini` (fastest/cheapest)

---

## Quick Start (Local Development)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Lab2FHIR.git
cd Lab2FHIR
```

### 2. Set Up Database

**Option A: Using Docker (recommended)**

```bash
docker run --name lab2fhir-db \
  -e POSTGRES_USER=lab2fhir \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=lab2fhir \
  -p 5432:5432 \
  -d postgres:14-alpine
```

**Option B: Using local PostgreSQL**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE lab2fhir;
CREATE USER lab2fhir WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE lab2fhir TO lab2fhir;
\q
```

### 3. Configure Environment

Create `.env` file in project root:

```bash
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://lab2fhir:changeme@localhost:5432/lab2fhir

# LLM Configuration (choose one)
OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# LLM_PROVIDER=openai  # Options: openai, anthropic, local
# LLM_MODEL=gpt-4o     # Default model for PDF parsing

# Optional: FHIR Server Integration (not required for MVP)
# FHIR_SERVER_URL=http://localhost:8080/fhir
# FHIR_SERVER_AUTH_TOKEN=

# Application Settings
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
```

**Important**: Replace `sk-your-key-here` with your actual OpenAI API key.

### 4. Install Backend Dependencies

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
# Initialize Alembic (if not already initialized)
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 6. Start Backend Server

```bash
# Make sure you're in backend/ directory with venv activated
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 7. Verify Backend is Running

Open browser to http://localhost:8000/docs - you should see the Swagger UI API documentation.

### 8. Install Frontend Dependencies (Optional)

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:3000

---

## First Steps: Process Your First Lab PDF

### Step 1: Create a Patient Profile

```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "John Doe",
    "patient_type": "human",
    "notes": "Test patient"
  }'
```

Save the returned `id` (UUID) - you'll need it for the upload.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "display_name": "John Doe",
  "patient_type": "human",
  "created_at": "2024-02-14T10:30:00Z"
}
```

### Step 2: Upload a Lab PDF

```bash
curl -X POST http://localhost:8000/api/uploads \
  -F "file=@/path/to/your/lab-report.pdf" \
  -F "patient_id=550e8400-e29b-41d4-a716-446655440000"
```

Save the returned `upload_id`.

**Response:**
```json
{
  "upload_id": "660e9500-f39c-52e5-b827-557766551111",
  "status": "uploaded",
  "file_name": "lab-report.pdf"
}
```

### Step 3: Monitor Processing Status

```bash
curl http://localhost:8000/api/uploads/660e9500-f39c-52e5-b827-557766551111
```

Status will progress through:
- `uploaded` → `extracting` → `parsing` → `review_pending`

Processing typically takes 10-30 seconds depending on PDF size and LLM API latency.

### Step 4: Review Intermediate Representation

```bash
curl http://localhost:8000/api/uploads/660e9500-f39c-52e5-b827-557766551111/intermediate
```

**Example Response:**
```json
{
  "lab_metadata": {
    "lab_name": "Quest Diagnostics",
    "clia_number": "05D0987654"
  },
  "collection_date": "2024-02-01T08:30:00Z",
  "analytes": [
    {
      "name": "Glucose",
      "value": 95.0,
      "unit": "mg/dL",
      "reference_range": "70-100",
      "status": "normal"
    }
  ]
}
```

**Verify the extracted data matches your PDF!**

### Step 5: (Optional) Edit Intermediate Representation

If you notice errors in the extracted data:

```bash
curl -X PUT http://localhost:8000/api/uploads/660e9500-f39c-52e5-b827-557766551111/intermediate \
  -H "Content-Type: application/json" \
  -d '{
    "lab_metadata": {...},
    "collection_date": "2024-02-01T08:30:00Z",
    "analytes": [
      {
        "name": "Glucose",
        "value": 85.0,
        "unit": "mg/dL",
        "reference_range": "70-100",
        "status": "normal"
      }
    ]
  }'
```

### Step 6: Generate FHIR Bundle

```bash
curl -X POST http://localhost:8000/api/uploads/660e9500-f39c-52e5-b827-557766551111/generate-fhir
```

### Step 7: Download FHIR Bundle

```bash
curl http://localhost:8000/api/uploads/660e9500-f39c-52e5-b827-557766551111/fhir \
  -o lab-bundle.json
```

### Step 8: View or Upload to FHIR Server

**View locally:**
```bash
cat lab-bundle.json | jq .
```

**Upload to FHIR server (e.g., Fasten, HAPI FHIR):**
```bash
curl -X POST https://your-fhir-server.com/fhir \
  -H "Content-Type: application/fhir+json" \
  -d @lab-bundle.json
```

**Success!** 🎉 You've converted your first lab PDF to FHIR resources.

---

## Using the Web UI (Optional)

If you installed the frontend:

1. Open http://localhost:3000
2. Click "Create Patient" → Enter name → Save
3. Click "Upload Lab Report" → Select patient → Choose PDF → Upload
4. Review intermediate data → Make corrections if needed → Confirm
5. Download FHIR Bundle

---

## Development Workflows

### Running Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/
```

### Code Quality Checks

```bash
# Linting and formatting with ruff
ruff check src/
ruff format src/

# Type checking with mypy
mypy src/

# Run all quality checks
ruff check src/ && ruff format --check src/ && mypy src/ && pytest
```

### Database Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Add new field to uploads table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Adding New Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install new package
pip install package-name

# Update requirements
pip freeze > requirements.txt
```

### Debugging

```bash
# Run with debug logging
LOG_LEVEL=DEBUG uvicorn src.main:app --reload

# Access database directly
psql postgresql://lab2fhir:changeme@localhost:5432/lab2fhir

# View recent uploads
SELECT id, file_name, status, created_at FROM uploads ORDER BY created_at DESC LIMIT 10;

# View intermediate representations
SELECT upload_id, version, is_edited, created_at FROM intermediate_representations ORDER BY created_at DESC LIMIT 5;
```

---

## Docker Deployment (Production)

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### 1. Create Production Environment File

```bash
cp .env .env.production

# Edit .env.production with production values
# - Use strong database password
# - Use production FHIR server URLs
# - Set appropriate CORS origins
```

### 2. Build and Start Services

```bash
# Build images
docker-compose build

# Start all services (PostgreSQL + Backend + Frontend)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 3. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Verify Services

```bash
# Check service status
docker-compose ps

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

### 5. Backup Database

```bash
# Backup
docker-compose exec db pg_dump -U lab2fhir lab2fhir > backup.sql

# Restore
docker-compose exec -T db psql -U lab2fhir lab2fhir < backup.sql
```

### 6. Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Apply migrations
docker-compose exec backend alembic upgrade head
```

---

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key for GPT models |
| `ANTHROPIC_API_KEY` | Yes* | - | Anthropic API key for Claude models |
| `LLM_PROVIDER` | No | `openai` | LLM provider: `openai`, `anthropic`, `local` |
| `LLM_MODEL` | No | `gpt-4o` | Model name for PDF parsing |
| `LLM_TEMPERATURE` | No | `0.1` | LLM temperature (0.0-1.0) |
| `LLM_MAX_TOKENS` | No | `4096` | Maximum tokens for LLM response |
| `FHIR_SERVER_URL` | No | - | Optional FHIR server for auto-upload |
| `FHIR_SERVER_AUTH_TOKEN` | No | - | Auth token for FHIR server |
| `LOG_LEVEL` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins (comma-separated) |
| `MAX_UPLOAD_SIZE_MB` | No | `10` | Maximum PDF upload size in MB |
| `DATABASE_POOL_SIZE` | No | `5` | PostgreSQL connection pool size |

*One of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` required unless using local LLM.

### LLM Provider Configuration

**OpenAI (Recommended):**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o  # or gpt-4o-mini for cost savings
```

**Anthropic:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
LLM_MODEL=claude-3-5-sonnet-20241022
```

**Local LLM (Advanced):**
```bash
LLM_PROVIDER=local
LLM_BASE_URL=http://localhost:11434/v1  # Example: Ollama
LLM_MODEL=llama3.1:70b
# No API key required for local
```

---

## Troubleshooting

### Issue: Database connection fails

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solutions:**
1. Verify PostgreSQL is running: `docker ps` or `pg_isready`
2. Check DATABASE_URL format: `postgresql://user:password@host:port/database`
3. Ensure database exists: `psql -l | grep lab2fhir`
4. Check firewall/network: `telnet localhost 5432`

### Issue: LLM parsing fails

**Symptoms:**
```
OpenAIError: Rate limit exceeded
```
or
```
Upload status stuck at "parsing"
```

**Solutions:**
1. Verify API key is set: `echo $OPENAI_API_KEY`
2. Check API key validity: https://platform.openai.com/api-keys
3. Review rate limits: https://platform.openai.com/account/rate-limits
4. Try different model: `LLM_MODEL=gpt-4o-mini`
5. Check upload logs: `curl http://localhost:8000/api/uploads/{upload_id}/logs`

### Issue: PDF extraction returns empty text

**Symptoms:**
```json
{
  "status": "failed",
  "error": "No text extracted from PDF"
}
```

**Solutions:**
1. Verify PDF is text-based (not scanned image)
2. Try OCR preprocessing (coming in future version)
3. Check PDF file integrity: `pdfinfo your-file.pdf`
4. Review extraction service logs

### Issue: FHIR validation errors

**Symptoms:**
```
ValidationError: Observation.code is required
```

**Solutions:**
1. Review intermediate representation completeness
2. Check analyte names are properly extracted
3. Verify units are UCUM-compliant
4. Examine generated FHIR bundle: `curl .../fhir | jq .`
5. Validate against FHIR spec: https://www.hl7.org/fhir/validation.html

### Issue: Port already in use

**Symptoms:**
```
Error: [Errno 48] Address already in use
```

**Solutions:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn src.main:app --port 8001
```

### Issue: Docker Compose fails to start

**Symptoms:**
```
ERROR: Service 'backend' failed to build
```

**Solutions:**
1. Check Docker is running: `docker ps`
2. Verify Docker Compose version: `docker-compose --version` (need 2.0+)
3. Clean up old containers: `docker-compose down -v`
4. Rebuild from scratch: `docker-compose build --no-cache`
5. Check logs: `docker-compose logs backend`

### Getting Help

1. **Check logs**: Backend logs contain detailed error messages
   ```bash
   tail -f logs/app.log  # Local development
   docker-compose logs -f backend  # Docker deployment
   ```

2. **Enable debug mode**: Set `LOG_LEVEL=DEBUG` in `.env`

3. **Review API documentation**: http://localhost:8000/docs

4. **Search issues**: https://github.com/yourusername/Lab2FHIR/issues

5. **Ask for help**: https://github.com/yourusername/Lab2FHIR/discussions

---

## Next Steps

### Customize for Your Lab Reports

1. **Add custom analyte mappings**: Edit `src/services/normalizer.py`
2. **Extend intermediate schema**: Update `contracts/intermediate-schema.json`
3. **Configure unit conversions**: Add to `src/services/unit_converter.py`

### Integrate with Your FHIR Server

1. Set `FHIR_SERVER_URL` in `.env`
2. Configure authentication: `FHIR_SERVER_AUTH_TOKEN`
3. Enable auto-upload: Set `AUTO_UPLOAD_TO_FHIR=true`

### Scale for Multiple Users

1. Add authentication: Implement OAuth2/OIDC
2. Multi-tenancy: Add user_id to patient and upload tables
3. Horizontal scaling: Run multiple backend replicas behind load balancer
4. Database optimization: Add indexes, connection pooling

### Advanced Features

- **Batch processing**: Upload multiple PDFs at once
- **OCR support**: Process scanned/image-based PDFs
- **Custom FHIR profiles**: Support specialty lab formats
- **Analytics dashboard**: Visualize lab trends over time
- **FHIR subscription**: Auto-sync to external EHR systems

---

## Resources

- **FHIR R4 Specification**: https://www.hl7.org/fhir/
- **FHIR Observation Resource**: https://www.hl7.org/fhir/observation.html
- **UCUM Units**: https://ucum.org/
- **LOINC Codes**: https://loinc.org/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/

---

## License

MIT License - See LICENSE file for details

---

**Questions?** Open an issue on GitHub or check the documentation at `/docs/README.md`
