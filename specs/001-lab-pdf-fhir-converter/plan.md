# Implementation Plan: Lab PDF to FHIR Converter

**Branch**: `001-lab-pdf-fhir-converter` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-lab-pdf-fhir-converter/spec.md`

**Note**: This plan implements Python + PostgreSQL backend for Lab2FHIR converter.

## Summary

Build a self-hosted pipeline that converts structured laboratory PDF reports into FHIR-compliant clinical resources for personal and household health record management. The system will use Python 3.11+ with FastAPI for the web interface, PostgreSQL for persistence, and structured LLM prompting for PDF extraction. An intermediate JSON schema will decouple extraction from FHIR generation to ensure validation and deterministic transformations.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), SQLAlchemy (ORM), Pydantic (validation), PyPDF2 or pdfplumber (PDF text extraction), FHIR.resources (FHIR R4 models), httpx (HTTP client for LLM APIs)
**Storage**: PostgreSQL 14+ (relational DB for pipeline state, patient profiles, intermediate representations, audit logs)
**Testing**: pytest (unit/integration tests), pytest-asyncio (async tests), pytest-postgresql (test DB fixtures)
**Target Platform**: Linux server (Docker container for self-hosted deployment)
**Project Type**: Web application (FastAPI backend + minimal web UI for upload/review)
**Performance Goals**: Process single PDF in <30 seconds (including LLM extraction), support <10 concurrent uploads
**Constraints**: Self-hosted operation (no mandatory cloud services), configurable LLM providers via environment variables, PHI-safe (no external data transmission except to configured services)
**Scale/Scope**: Household scale (5-10 patient profiles, 100s of lab reports per year, <1GB storage per patient)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**✓ Deterministic behavior**: 
- PDF text extraction: Deterministic (same PDF → same text output)
- LLM extraction: Non-deterministic at extraction, but validated through strict intermediate schema
- Normalization: Deterministic (UCUM unit normalization, analyte name canonicalization)
- Deduplication keys: Deterministic (based on subject + collection date + analyte + value + unit)
- FHIR generation: Deterministic (same intermediate JSON → same FHIR Bundle)

**✓ Intermediate schema enforcement**: 
- Strict JSON Schema defined for intermediate representation
- LLM outputs structured JSON matching intermediate schema
- Schema validation occurs immediately after LLM extraction
- Schema validation occurs again before FHIR conversion
- Direct LLM-to-FHIR prohibited by architecture

**✓ PDF preservation & FHIR traceability**: 
- Source PDFs stored in PostgreSQL (BYTEA column) with SHA-256 hash
- DocumentReference resource created for each PDF
- DiagnosticReport links to DocumentReference
- Each Observation includes deterministic identifier and provenance reference
- Audit log tracks: upload → extraction → validation → FHIR generation

**✓ PHI-safe, self-hosted operation**: 
- Configurable LLM provider via environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY, or local endpoint)
- PostgreSQL database runs locally (Docker Compose)
- No mandatory external services beyond user-configured LLM
- All sensitive configuration externalized (DATABASE_URL, LLM config, FHIR endpoints)

**✓ Minimal infrastructure**: 
- Python + PostgreSQL (no additional services for MVP)
- FastAPI web server (single process, can scale horizontally if needed)
- Optional FHIR server integration (not mandatory, configured via env)
- Replaceable LLM provider through configuration

**✓ Validation evidence**: 
- Unit tests: pytest for models, services, FHIR generation
- Integration tests: pytest with test PostgreSQL database
- Contract tests: JSON Schema validation, FHIR Bundle validation
- Linting: ruff (formatter + linter)
- Type checking: mypy
- Results recorded in CI logs and local test output

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLAlchemy models (Patient, Upload, IntermediateRep, FHIRBundle)
│   ├── schemas/         # Pydantic schemas (intermediate JSON schema, API request/response)
│   ├── services/        # Business logic (pdf_extractor, llm_parser, normalizer, fhir_generator)
│   ├── api/             # FastAPI routes (upload, review, generate, download)
│   ├── db/              # Database connection, migrations (Alembic)
│   └── config.py        # Configuration (env vars, LLM provider settings)
├── tests/
│   ├── contract/        # JSON Schema validation, FHIR Bundle validation
│   ├── integration/     # End-to-end pipeline tests with test DB
│   └── unit/            # Service and model unit tests
├── migrations/          # Alembic database migrations
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project metadata, tool configuration (ruff, mypy)
└── Dockerfile           # Container build

frontend/
├── src/
│   ├── components/      # React/HTML components (UploadForm, IntermediateReview, BundleDownload)
│   ├── pages/           # Main pages (Upload, Review, History)
│   └── services/        # API client for backend
├── tests/
└── package.json

docker-compose.yml       # PostgreSQL + backend + frontend services
README.md                # Setup and deployment instructions
```

**Structure Decision**: Web application with backend/frontend split. Backend handles all PDF processing, LLM interaction, database persistence, and FHIR generation. Frontend provides minimal web UI for upload, review, and download. This structure supports self-hosted deployment via Docker Compose and allows frontend replacement without affecting core pipeline logic.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitutional principles are satisfied by the proposed architecture.
