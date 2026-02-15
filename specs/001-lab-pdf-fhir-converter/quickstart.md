# Quickstart: Lab PDF to FHIR Converter (Python + Postgres + Heroku)

## Prerequisites
- Python 3.12
- PostgreSQL 16
- Node.js 20+ (for frontend)
- Heroku CLI (for deployment)

## 1) Configure environment
Create `.env` files for backend and frontend.

Backend required environment variables:
- `DATABASE_URL=postgresql+psycopg://...`
- `APP_ENV=development`
- `SECRET_KEY=<random>`
- `PDF_STORAGE_PATH=./data/pdfs` (or object storage URI)
- `LLM_PROVIDER=local|openai|...`
- `LLM_MODEL=<model-name>`
- `FHIR_SUBMISSION_MODE=manual` (MVP default)

Optional P5 variables:
- `FHIR_BASE_URL=https://.../fhir`
- `FHIR_AUTH_TYPE=none|basic`
- `FHIR_BASIC_USERNAME=...`
- `FHIR_BASIC_PASSWORD=...`

## 2) Install dependencies
Backend:
- `cd backend`
- `pip install -r requirements.txt`
- `alembic upgrade head`

Frontend:
- `cd frontend`
- `npm install`

## 3) Run locally
- Start backend: `cd backend && uvicorn src.main:app --reload`
- Start frontend: `cd frontend && npm run dev`

## 4) Run validation checks
- Backend lint: `cd backend && ruff check .`
- Backend tests: `cd backend && pytest`
- Contract checks: `cd backend && pytest tests/contract`

## 5) Manual MVP workflow test
1. Create a patient profile.
2. Upload a text-based PDF lab report.
3. Confirm status reaches `review_pending`.
4. Review/edit intermediate JSON and save.
5. Generate bundle and download JSON.
6. Validate bundle imports to your target FHIR store.

## 6) Deploy to Heroku (initial)
- Create app: `heroku create <app-name>`
- Add Postgres: `heroku addons:create heroku-postgresql:essential-0`
- Set config vars: `heroku config:set DATABASE_URL=... SECRET_KEY=... LLM_PROVIDER=... LLM_MODEL=... FHIR_SUBMISSION_MODE=manual`
- Deploy: `git push heroku main`
- Run migrations: `heroku run -a <app-name> alembic upgrade head`

## 7) Post-deploy smoke checks
- Upload one known-good text PDF.
- Verify duplicate upload is blocked by file hash.
- Confirm Observation -> DiagnosticReport -> DocumentReference traceability in downloaded bundle.

## 8) FHIR mapping conformance checklist
Use this checklist on a generated bundle to verify model-to-FHIR mapping conformance.

- Bundle-level checks:
	- `Bundle.type` is `transaction`.
	- Bundle contains exactly one `Patient`, one `DocumentReference`, one `DiagnosticReport`, and `>=1` `Observation`.
	- Bundle entry order is deterministic: `Patient`, `DocumentReference`, `DiagnosticReport`, then `Observation[]` sorted by deterministic key.

- Patient mapping checks:
	- `Patient.identifier[0].system == urn:lab2fhir:subject-id`.
	- `Patient.identifier[0].value` matches `external_subject_id`.
	- `Patient.name[0].text` matches `display_name`.

- DocumentReference mapping checks:
	- `DocumentReference.status == current` and `DocumentReference.docStatus == final`.
	- `DocumentReference.content[0].attachment.contentType` matches source PDF MIME type.
	- `DocumentReference.content[0].attachment.title` matches original filename.
	- `DocumentReference.identifier[0].system == urn:lab2fhir:file-sha256`.
	- `DocumentReference.content[0].attachment.hash` equals base64(raw-bytes(hex-SHA256)).

- DiagnosticReport mapping checks:
	- `DiagnosticReport.status == final`.
	- `DiagnosticReport.subject` references the same `Patient` as all derived observations.
	- `DiagnosticReport.result[]` includes references to all generated observations.

- Observation mapping checks:
	- `Observation.status == final` for all observations.
	- `Observation.effectiveDateTime` maps from per-measurement `collectionDateTime`.
	- `Observation.issued` maps from per-measurement `resultDateTime` (or falls back to `collectionDateTime`).
	- `Observation.code.coding[0].code` maps from `normalizedAnalyteCode`.
	- `Observation.valueQuantity` is used for numeric/operator-numeric values; `Observation.valueString` for qualitative values.
	- If UCUM normalization exists, `Observation.valueQuantity.system == http://unitsofmeasure.org`.

- Determinism checks:
	- Re-running generation with identical parsed input yields identical Observation IDs.
	- Re-generated bundles from unchanged parsed versions produce stable resource IDs and equivalent content.
