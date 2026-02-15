# Phase 0 Research: Lab PDF to FHIR Converter

## Decision 1: Backend framework and runtime
- Decision: Use FastAPI on Python 3.12.
- Rationale: FastAPI provides strong request/response typing, OpenAPI generation, and async support suitable for upload + processing workflows and Heroku deployment.
- Alternatives considered: Django (heavier for this API-first flow), Flask (less built-in validation and schema tooling).

## Decision 2: Persistence model on Heroku
- Decision: Use Heroku Postgres (PostgreSQL 16) for operational data and metadata, and persist source PDFs using object/file storage abstraction.
- Rationale: Postgres is managed on Heroku, supports transactional guarantees and audit-friendly history tables; storage abstraction keeps deployment portable.
- Alternatives considered: SQLite (not suitable for concurrent production workloads), MongoDB (weaker relational/audit patterns for this domain).

## Decision 3: PDF parsing and scanned-document rejection
- Decision: Use `pdfplumber` text extraction and classify scanned/image PDFs when extracted text density falls below threshold and pages are image-only.
- Rationale: `pdfplumber` handles text-based clinical PDFs reliably and enables deterministic extraction checks before LLM parsing.
- Alternatives considered: OCR-first pipeline (outside MVP scope and violates minimal infrastructure), `PyPDF2`/`pypdf` only (less reliable for table-like lab layouts).

## Decision 4: Intermediate schema and validation boundary
- Decision: Define strict Pydantic v2 schema for parsed lab data; require parser output to pass schema validation before normalization and FHIR mapping.
- Rationale: Enforces constitution rule against direct model-to-FHIR conversion and provides deterministic contract tests.
- Alternatives considered: Ad-hoc dict validation (higher drift risk), JSON Schema-only runtime checks without typed domain model.

## Decision 5: LLM integration strategy
- Decision: Provider-agnostic adapter with constrained JSON output (function-calling/response schema mode), configurable for local or API providers.
- Rationale: Meets PHI/self-hosted requirements while preserving a stable parser interface.
- Alternatives considered: Hard-coded single SaaS model provider, prompt-only free-form parsing.

## Decision 6: Deterministic deduplication and identifiers
- Decision: Use SHA-256 file hash for upload-level dedup and deterministic Observation ID seed `{subject}|{collection_datetime}|{normalized_analyte}|{value}|{unit}`.
- Rationale: Prevents duplicate processing and duplicate clinical observations across reimports.
- Alternatives considered: Random UUIDs only (non-deterministic), fuzzy duplicate detection (non-deterministic false positives).

## Decision 7: FHIR generation library
- Decision: Use `fhir.resources` for R4 resource structure validation with final bundle-level validation in integration tests.
- Rationale: Reduces hand-built JSON errors and supports typed resource composition.
- Alternatives considered: Manual JSON templates (higher defect risk), full FHIR server-in-the-loop generation for MVP.

## Decision 8: Asynchronous processing pattern
- Decision: Use durable PostgreSQL-backed job records with leasing semantics for parse/generate work, with API requests enqueueing jobs and returning status.
- Rationale: Preserves minimal infrastructure while surviving process restarts and enabling reliable retries/status tracking.
- Alternatives considered: FastAPI in-process background tasks only (risk of lost work on restart), Celery/Redis queues (more infra than needed for MVP), fully synchronous upload request (poor UX/timeouts).

## Decision 9: API contract style
- Decision: REST API with explicit status resources and downloadable bundle endpoints.
- Rationale: Directly maps to upload/review/edit/generate/download/regenerate user actions and is simple for web UI integration.
- Alternatives considered: GraphQL (overhead for mutation-heavy workflow), RPC-only endpoints without resource modeling.

## Decision 10: Deployment baseline
- Decision: Deploy as Heroku container or buildpack app with runtime config from environment variables and managed Postgres.
- Rationale: Aligns with initial deployment requirement and keeps self-hosted portability for later migration.
- Alternatives considered: Kubernetes-first deployment (overly complex), serverless multi-service architecture.
