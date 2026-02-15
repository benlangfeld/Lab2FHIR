# Tasks: Lab PDF to FHIR Converter

**Input**: Design documents from `/specs/001-lab-pdf-fhir-converter/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize backend/frontend projects, tooling, and baseline test scaffolding.

- [ ] T001 Create backend project scaffolding and package metadata in backend/pyproject.toml
- [ ] T002 Create frontend project scaffolding and package metadata in frontend/package.json
- [ ] T003 [P] Configure backend lint/test tool settings in backend/pyproject.toml
- [ ] T004 [P] Add backend test directory scaffolding with init files in backend/tests/__init__.py
- [ ] T005 [P] Create synthetic fixture directories in backend/tests/fixtures/README.md
- [ ] T006 [P] Add base environment template for runtime settings in backend/.env.example
- [ ] T007 [P] Add Alembic baseline configuration in backend/alembic.ini
- [ ] T008 Add developer run/test commands to feature quickstart in specs/001-lab-pdf-fhir-converter/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement core architecture required before any user story work.

**⚠️ CRITICAL**: No user story work starts before this phase completes.

- [ ] T009 Create SQLAlchemy base/session and DB wiring in backend/src/db/session.py
- [ ] T010 [P] Implement core ORM entities for PatientProfile and LabReport in backend/src/db/models/reporting.py
- [ ] T011 [P] Implement ORM entities for ParsedLabDataVersion, FhirBundleArtifact, SubmissionRecord, EditHistoryEntry in backend/src/db/models/pipeline.py
- [ ] T012 Create initial migration for core tables and indexes in backend/alembic/versions/0001_initial_schema.py
- [ ] T013 Implement report state machine and transition guard utility in backend/src/domain/report_state_machine.py
- [ ] T014 [P] Define intermediate schema models (payload + measurement) in backend/src/domain/intermediate_schema.py
- [ ] T015 [P] Implement deterministic ID and normalization utilities in backend/src/domain/determinism.py
- [ ] T016 [P] Implement FHIR projection defaults and mapping helpers in backend/src/domain/fhir_mapping.py
- [ ] T017 Create storage abstraction for source PDFs and bundle artifacts in backend/src/services/storage_service.py
- [ ] T018 Create API error taxonomy and shared exception handlers in backend/src/api/errors.py
- [ ] T019 Create FastAPI app bootstrap, router registration, and middleware in backend/src/main.py
- [ ] T020 Add foundational unit tests for schema validation/state machine/determinism in backend/tests/unit/test_foundation.py

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Upload and Process Single Lab Report (Priority: P1) 🎯 MVP

**Goal**: Upload a text-based PDF, parse to validated intermediate JSON, and generate/download a FHIR bundle.

**Independent Test**: Upload one fixture PDF, verify `review_pending`, inspect parsed JSON, generate bundle, download valid FHIR JSON.

### Tests for User Story 1

- [ ] T021 [P] [US1] Add contract test for report upload/status endpoints in backend/tests/contract/test_reports_upload_status.py
- [ ] T022 [P] [US1] Add contract test for bundle generation/download endpoints in backend/tests/contract/test_bundle_generation_download.py
- [ ] T023 [P] [US1] Add integration test for upload→parse→generate→download happy path in backend/tests/integration/test_us1_happy_path.py
- [ ] T024 [P] [US1] Add synthetic fixture PDF and expected parsed snapshot in backend/tests/fixtures/us1/lab_numeric_basic.pdf

### Implementation for User Story 1

- [ ] T025 [US1] Implement patient create/list API endpoints in backend/src/api/patients.py
- [ ] T026 [US1] Implement report upload endpoint with hash calculation and persistence in backend/src/api/reports.py
- [ ] T027 [US1] Implement text extraction and scanned-PDF rejection logic in backend/src/services/pdf_extraction_service.py
- [ ] T028 [US1] Implement provider-agnostic parser adapter with constrained schema output in backend/src/services/parser_service.py
- [ ] T029 [US1] Implement parse pipeline orchestration and status transitions in backend/src/services/report_pipeline_service.py
- [ ] T030 [US1] Implement get parsed data endpoint in backend/src/api/parsed_data.py
- [ ] T031 [US1] Implement FHIR bundle generation service (DocumentReference + DiagnosticReport + Observation) in backend/src/services/fhir_bundle_service.py
- [ ] T032 [US1] Implement generate-bundle and download-bundle endpoints in backend/src/api/bundles.py
- [ ] T033 [US1] Implement report history and single report status endpoints in backend/src/api/reports.py

**Checkpoint**: US1 is independently functional and testable.

---

## Phase 4: User Story 2 - Correct Mistaken Parsing (Priority: P2)

**Goal**: Allow editing intermediate JSON with schema validation and audit history, then generate corrected bundle.

**Independent Test**: Edit a parsed value, save valid correction, generate bundle, verify corrected value appears.

### Tests for User Story 2

- [ ] T034 [P] [US2] Add contract test for parsed-data update validation behavior in backend/tests/contract/test_parsed_data_update_validation.py
- [ ] T035 [P] [US2] Add integration test for correction workflow and corrected bundle projection in backend/tests/integration/test_us2_manual_corrections.py

### Implementation for User Story 2

- [ ] T036 [US2] Implement parsed-data update endpoint with strict schema validation in backend/src/api/parsed_data.py
- [ ] T037 [US2] Implement corrected version creation logic (append-only) in backend/src/services/parsed_data_service.py
- [ ] T038 [US2] Implement edit history persistence for changed fields in backend/src/services/edit_history_service.py
- [ ] T039 [US2] Ensure bundle generation selects latest valid parsed version in backend/src/services/fhir_bundle_service.py
- [ ] T040 [US2] Add frontend edit/review workflow UI for parsed JSON in frontend/src/pages/report-review.tsx
- [ ] T041 [US2] Add frontend schema-error highlighting and save handling in frontend/src/components/parsed-json-editor.tsx

**Checkpoint**: US1 and US2 both work independently.

---

## Phase 5: User Story 3 - Prevent Duplicate Imports (Priority: P2)

**Goal**: Detect duplicate uploads and prevent duplicate processing while preserving audit records.

**Independent Test**: Upload same PDF twice; second attempt is marked duplicate and no new bundle generated.

### Tests for User Story 3

- [ ] T042 [P] [US3] Add contract test for duplicate upload response/status in backend/tests/contract/test_duplicate_uploads.py
- [ ] T043 [P] [US3] Add integration test for duplicate detection and audit linkage in backend/tests/integration/test_us3_duplicate_imports.py

### Implementation for User Story 3

- [ ] T044 [US3] Add unique hash lookup and duplicate linkage behavior in backend/src/services/report_pipeline_service.py
- [ ] T045 [US3] Implement duplicate status transition handling in backend/src/domain/report_state_machine.py
- [ ] T046 [US3] Add duplicate-specific API error/message mapping in backend/src/api/errors.py
- [ ] T047 [US3] Add duplicate upload fixture set in backend/tests/fixtures/us3/
- [ ] T048 [US3] Update frontend upload feedback for duplicate reports in frontend/src/components/upload-form.tsx

**Checkpoint**: US3 independently prevents duplicate imports.

---

## Phase 6: User Story 4 - Normalize Units Across Time (Priority: P2)

**Goal**: Normalize analyte names/units for longitudinal comparability while preserving originals.

**Independent Test**: Process reports with same analyte in different units and verify normalized outputs are comparable.

### Tests for User Story 4

- [ ] T049 [P] [US4] Add unit tests for analyte/unit normalization rules in backend/tests/unit/test_normalization_rules.py
- [ ] T050 [P] [US4] Add integration test for cross-report unit normalization in backend/tests/integration/test_us4_unit_normalization.py

### Implementation for User Story 4

- [ ] T051 [US4] Implement canonical analyte normalization map and resolver in backend/src/domain/analyte_normalization.py
- [ ] T052 [US4] Implement UCUM-oriented unit normalization/conversion rules in backend/src/domain/unit_normalization.py
- [ ] T053 [US4] Integrate normalization stage into parse-to-FHIR pipeline in backend/src/services/report_pipeline_service.py
- [ ] T054 [US4] Ensure original and normalized values are both persisted in parsed payload in backend/src/services/parser_service.py
- [ ] T055 [US4] Add synthetic mixed-unit fixtures and expected snapshots in backend/tests/fixtures/us4/

**Checkpoint**: US4 independently delivers consistent normalized outputs.

---

## Phase 7: User Story 5 - Preserve Original Documents (Priority: P3)

**Goal**: Ensure source PDF is preserved and traceable from generated FHIR resources.

**Independent Test**: Retrieve original PDF for processed report and verify byte-equivalence with upload.

### Tests for User Story 5

- [ ] T056 [P] [US5] Add integration test for source PDF preservation and retrieval parity in backend/tests/integration/test_us5_pdf_preservation.py
- [ ] T057 [P] [US5] Add unit test for attachment hash conversion (hex→base64 bytes) in backend/tests/unit/test_documentreference_hash.py

### Implementation for User Story 5

- [ ] T058 [US5] Implement durable PDF persistence and retrieval service paths in backend/src/services/storage_service.py
- [ ] T059 [US5] Add DocumentReference content + hash mapping in backend/src/services/fhir_bundle_service.py
- [ ] T060 [US5] Ensure DiagnosticReport links to source document via deterministic mapping extension/reference in backend/src/domain/fhir_mapping.py
- [ ] T061 [US5] Add API endpoint for retrieving original source document metadata/content in backend/src/api/reports.py

**Checkpoint**: US5 independently guarantees source traceability.

---

## Phase 8: User Story 6 - Re-generate FHIR Bundle from Intermediate Representation (Priority: P4)

**Goal**: Regenerate bundles from stored parsed data without re-parsing PDFs.

**Independent Test**: Trigger regenerate on completed report and verify new bundle generated from stored parsed version.

### Tests for User Story 6

- [ ] T062 [P] [US6] Add contract test for regenerate-bundle endpoint behavior in backend/tests/contract/test_regenerate_bundle.py
- [ ] T063 [P] [US6] Add integration test for regenerate using corrected parsed version in backend/tests/integration/test_us6_regeneration.py

### Implementation for User Story 6

- [ ] T064 [US6] Implement regenerate orchestration that bypasses parser stage in backend/src/services/report_pipeline_service.py
- [ ] T065 [US6] Persist regeneration artifacts with generation_mode metadata in backend/src/services/fhir_bundle_service.py
- [ ] T066 [US6] Implement regenerate-bundle API endpoint and status transitions in backend/src/api/bundles.py
- [ ] T067 [US6] Add frontend regenerate action in processing history UI in frontend/src/pages/report-history.tsx

**Checkpoint**: US6 independently enables deterministic regeneration.

---

## Phase 9: User Story 7 - Handle Multiple Patients (Priority: P4)

**Goal**: Support multiple human/veterinary patient profiles and proper subject association in bundles.

**Independent Test**: Create multiple profiles, upload per subject, and verify subject references in generated bundles.

### Tests for User Story 7

- [ ] T068 [P] [US7] Add contract test for patient create/list and upload selection behavior in backend/tests/contract/test_multi_patient_profiles.py
- [ ] T069 [P] [US7] Add integration test for multi-patient separation and subject mapping in backend/tests/integration/test_us7_multi_patient.py

### Implementation for User Story 7

- [ ] T070 [US7] Finalize patient profile service rules (identifier immutability/type validation) in backend/src/services/patient_service.py
- [ ] T071 [US7] Ensure upload pipeline requires valid patient selection in backend/src/api/reports.py
- [ ] T072 [US7] Ensure FHIR subject mapping for human/veterinary profiles in backend/src/domain/fhir_mapping.py
- [ ] T073 [US7] Add frontend patient management UI in frontend/src/pages/patients.tsx
- [ ] T074 [US7] Add patient selection controls in upload workflow UI in frontend/src/components/upload-form.tsx

**Checkpoint**: US7 independently supports household multi-patient workflows.

---

## Phase 10: User Story 8 - Automatic FHIR Store Integration (Priority: P5)

**Goal**: Optionally auto-submit generated bundles to configured FHIR endpoint with retries.

**Independent Test**: Configure FHIR endpoint, process report, and verify auto-submission status with retry handling.

### Tests for User Story 8

- [ ] T075 [P] [US8] Add contract test for submission status visibility in backend/tests/contract/test_fhir_submission_status.py
- [ ] T076 [P] [US8] Add integration test for successful auto-submit flow in backend/tests/integration/test_us8_auto_submit_success.py
- [ ] T077 [P] [US8] Add integration test for retry/failure flow in backend/tests/integration/test_us8_auto_submit_retry.py

### Implementation for User Story 8

- [ ] T078 [US8] Implement configurable FHIR submission client with auth modes in backend/src/services/fhir_submission_service.py
- [ ] T079 [US8] Implement submission record persistence and retry policy in backend/src/services/submission_tracking_service.py
- [ ] T080 [US8] Integrate optional auto-submit into bundle-complete pipeline in backend/src/services/report_pipeline_service.py
- [ ] T081 [US8] Expose submission status in report detail/history responses in backend/src/api/reports.py
- [ ] T082 [US8] Add frontend status indicators for auto-import outcomes in frontend/src/components/report-status-badge.tsx

**Checkpoint**: US8 independently enables optional automatic server integration.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, documentation, and final validation across stories.

- [ ] T083 [P] Add deterministic fixture naming conventions and coverage matrix in backend/tests/fixtures/README.md
- [ ] T084 [P] Add end-to-end conformance test for data-model-to-FHIR mapping checklist in backend/tests/integration/test_fhir_mapping_conformance.py
- [ ] T085 Add performance smoke test for <2 minute processing target in backend/tests/integration/test_processing_performance_smoke.py
- [ ] T086 [P] Update API contract docs/examples for implemented payloads and errors in specs/001-lab-pdf-fhir-converter/contracts/openapi.yaml
- [ ] T087 [P] Update quickstart execution steps with fixture-driven validation run in specs/001-lab-pdf-fhir-converter/quickstart.md
- [ ] T088 Re-run constitution compliance evidence and capture in specs/001-lab-pdf-fhir-converter/plan.md
- [ ] T089 Final implementation readiness review for PR scope in specs/001-lab-pdf-fhir-converter/tasks.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies.
- Phase 2 (Foundational): depends on Phase 1 and blocks all user stories.
- Phases 3-10 (User Stories): each depends on Phase 2; then run by priority or in parallel by team capacity.
- Phase 11 (Polish): depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: starts after Phase 2; no dependency on other stories.
- **US2 (P2)**: depends on US1 parsed-data baseline.
- **US3 (P2)**: depends on US1 upload pipeline baseline.
- **US4 (P2)**: depends on US1 parse pipeline baseline.
- **US5 (P3)**: depends on US1 bundle + storage baseline.
- **US6 (P4)**: depends on US1 and US2 parsed-version storage.
- **US7 (P4)**: can start after Phase 2 but integrates best with US1 upload flow.
- **US8 (P5)**: depends on US1 bundle generation and US5 traceability artifacts.

### Within Each User Story

- Tests first (contract/integration/unit) and confirm failures before implementation.
- Models/schemas before orchestration services.
- Services before API endpoints/UI wiring.
- Determinism and traceability checks before story sign-off.

---

## Parallel Opportunities

- Phase 1 tasks marked [P] can run in parallel.
- Phase 2 domain/model tasks marked [P] can run in parallel after DB/session baseline.
- In each story, contract/integration tests marked [P] can be authored in parallel.
- Frontend tasks can run in parallel with backend service tasks once API contracts are stable.

### Parallel Example: User Story 1

```bash
Task: "T021 [US1] Contract upload/status tests in backend/tests/contract/test_reports_upload_status.py"
Task: "T022 [US1] Contract bundle tests in backend/tests/contract/test_bundle_generation_download.py"
Task: "T024 [US1] Add synthetic fixture PDF in backend/tests/fixtures/us1/lab_numeric_basic.pdf"
```

### Parallel Example: User Story 2

```bash
Task: "T034 [US2] Contract parsed-data update validation in backend/tests/contract/test_parsed_data_update_validation.py"
Task: "T041 [US2] Frontend parsed JSON editor in frontend/src/components/parsed-json-editor.tsx"
```

### Parallel Example: User Story 8

```bash
Task: "T076 [US8] Auto-submit success integration test in backend/tests/integration/test_us8_auto_submit_success.py"
Task: "T077 [US8] Auto-submit retry integration test in backend/tests/integration/test_us8_auto_submit_retry.py"
Task: "T082 [US8] Frontend submission status indicator in frontend/src/components/report-status-badge.tsx"
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Deliver US1 end-to-end and validate independently.
4. Add US2 correction workflow and validate independently.
5. Add US3 duplicate prevention and validate independently.
6. Demo/deploy MVP slice.

### Incremental Delivery

1. Add US4 normalization after MVP for longitudinal quality.
2. Add US5 source preservation hardening and traceability tests.
3. Add US6 regeneration and US7 multi-patient support.
4. Add US8 optional auto-submit integration last.
5. Finish with Phase 11 cross-cutting hardening.

### Team Parallelization

1. One sub-team closes Phase 1-2.
2. Then parallel streams:
   - Stream A: US2 + US6
   - Stream B: US3 + US4
   - Stream C: US5 + US8
   - Stream D: US7 frontend-heavy flow

---

## Notes

- All tasks follow strict checklist format with Task ID, optional [P], optional [USx], and exact file path.
- Story phases are independently testable increments aligned to spec priorities.
- Synthetic fixtures are first-class artifacts for deterministic and contract testing.
- Use independent git commits per completed task (one task per commit) to preserve traceability and simplify review/revert workflows.
- Include the task ID in each commit message, for example: `T031 [US1] Implement FHIR bundle generation service`.
