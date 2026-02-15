# Implementation Plan: Lab PDF to FHIR Converter

**Branch**: `001-lab-pdf-fhir-converter` | **Date**: 2026-02-14 | **Spec**: `/specs/001-lab-pdf-fhir-converter/spec.md`
**Input**: Feature specification from `/specs/001-lab-pdf-fhir-converter/spec.md`

## Summary

Build a self-hosted web workflow that accepts text-based laboratory PDFs, extracts structured lab data into a validated intermediate schema, supports user review/correction, and generates downloadable FHIR R4 transaction bundles (DocumentReference, DiagnosticReport, Observation) with deterministic deduplication and end-to-end source traceability.

Implementation uses Python (FastAPI + Pydantic v2) and PostgreSQL for state/audit persistence, with local file/object storage abstraction for original PDFs and generated bundles.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**:
- Backend API: FastAPI, Uvicorn
- Validation/serialization: Pydantic v2
- Database: PostgreSQL 16, SQLAlchemy 2.x, Alembic, psycopg
- PDF text extraction: pdfplumber
- FHIR modeling/validation: fhir.resources (R4)
- Testing/linting: pytest, pytest-asyncio, ruff

**Storage**:
- Primary relational store: PostgreSQL (reports, parsed versions, bundle artifacts, audit records)
- Binary/document store: filesystem path abstraction (`PDF_STORAGE_PATH`) for source PDFs and downloaded bundle artifacts

**Testing**:
- Unit: schema validation, normalization, deterministic identifier generation
- Integration: upload→parse→review/edit→generate→download workflow
- Contract: OpenAPI request/response behavior and error taxonomy
- Determinism checks: same input produces stable dedup hash + bundle identifiers
- Fixtures: create synthetic text-based lab report PDF fixtures (no PHI) with expected intermediate JSON and expected FHIR bundle outputs for repeatable tests

**Target Platform**: Linux server/container (self-hosted baseline); deployable on Heroku/VPS/NAS/Mac Mini
**Project Type**: Web application (backend API + frontend web UI)
**Performance Goals**:
- End-to-end processing target: < 2 minutes per text-based report
- Status propagation target: visible state updates within 5 seconds

**Constraints**:
- PHI-safe operation in self-hosted environments
- No mandatory external SaaS dependency for core ingestion/generation workflow
- OCR for scanned/image PDFs explicitly out of MVP scope (must detect + reject)
- Deterministic dedup and identifier behavior required

**Scale/Scope**:
- Household-scale usage (multi-patient: humans + veterinary)
- Initial concurrency target: low-to-moderate (single household active sessions)
- Initial feature slice: P1/P2/P3 required for MVP; P4/P5 staged behind optional capability flags

## Implementation Clarifications

**Execution model (MVP)**:
- Parse and bundle generation run as durable background jobs persisted in PostgreSQL (`jobs` table + leasing semantics).
- API requests enqueue work and return immediately with report/job status.
- State transitions are enforced by an explicit report state machine; invalid transitions are rejected.

**Idempotency and dedup semantics**:
- File-level dedup: unique `file_hash_sha256` check prevents reprocessing identical files.
- Operation-level idempotency: generate/regenerate endpoints accept an idempotency key to avoid duplicate jobs on client retries.
- Clinical-level dedup: deterministic Observation identifier seed remains stable after normalization.

**Intermediate schema versioning**:
- Every parsed payload stores `schema_version`.
- New payload versions are append-only (`original` then `corrected` variants); no in-place mutation of prior versions.
- Regeneration uses the latest `valid` parsed version unless a specific version is requested.

**Normalization contract**:
- Canonicalization occurs before deterministic ID generation.
- Dates use ISO 8601 with timezone; units target UCUM-compatible normalized forms where mappings exist.
- Operator-based numeric values (`<`, `<=`, `>`, `>=`) preserve both operator and numeric value through normalization.

**Error taxonomy baseline**:
- All failed states return actionable error codes and messages (e.g., scanned PDF, schema validation failure, missing critical dates, duplicate upload).
- Contract tests must verify status code + error code mapping for each documented edge case.

**Synthetic fixture strategy**:
- Maintain curated synthetic PDF fixtures covering core paths: normal numeric labs, qualitative labs, operator-based values (`<`, `>`), multi-measurement panels, and duplicate-upload scenarios.
- For each fixture, store expected parsed payload snapshot and expected deterministic FHIR IDs to enforce stable transformations.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Deterministic behavior: PASS
  - SHA-256 file hash for upload deduplication
  - Deterministic observation key seed `{subject}|{collection_datetime}|{normalized_analyte}|{value}|{unit}`
  - Stable normalization ordering and bundle generation path
- Intermediate schema enforcement: PASS
  - Parsing output must conform to strict intermediate schema (Pydantic model)
  - FHIR conversion only accepts validated intermediate payloads
  - Direct model-to-FHIR generation prohibited
- PDF traceability: PASS
  - Source PDF stored and referenced in DocumentReference
  - Observation → DiagnosticReport → DocumentReference linkage preserved
- PHI-safe/self-hosted operation: PASS
  - Runtime configuration by environment variables
  - Local/provider-agnostic LLM adapter; no hard-coded vendor requirement
- Minimal infrastructure: PASS
  - FastAPI + Postgres + file storage baseline; no queue broker required in MVP
  - Optional integrations (auto-submit/retry) are feature-flagged
- Validation evidence: PASS
  - Lint: `ruff check backend`
  - Unit/Integration/Contract: `pytest backend/tests`
  - Contract-targeted: `pytest backend/tests/contract`
  - Results captured in CI logs and PR checks

### Post-Design Constitution Re-Check

- Deterministic Transformations: PASS (data model + research preserve deterministic dedup and ID generation)
- Validated Intermediate Schema: PASS (intermediate version entity + validation status enforced before bundle generation)
- PDF Preservation & Traceability: PASS (DocumentReference required; report stores source URI and hash)
- PHI-Safe Self-Hosted: PASS (config-driven LLM/FHIR endpoints; manual bundle download path is default)
- Minimal Infrastructure: PASS (no mandatory queue/OCR/third-party services in MVP)

## Project Structure

### Documentation (this feature)

```text
specs/001-lab-pdf-fhir-converter/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/             # FastAPI routers
│   ├── domain/          # intermediate schema, normalization, dedup rules
│   ├── services/        # parsing, bundle generation, storage adapters
│   ├── db/              # SQLAlchemy models, repositories, alembic config
│   └── main.py
└── tests/
    ├── fixtures/        # synthetic PDF fixtures + expected parsed/FHIR snapshots
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/        # API client + workflow actions
└── tests/
```

**Structure Decision**: Use a web-application split (`backend/` + `frontend/`) to isolate clinical transformation logic and persistence in Python while keeping UI workflow concerns separate. Backend is the source of truth for deterministic pipeline behavior and audit history.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
