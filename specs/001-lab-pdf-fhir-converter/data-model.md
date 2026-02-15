# Data Model: Lab PDF to FHIR Converter

## Entity: PatientProfile
- Fields:
  - `id` (UUID, PK)
  - `external_subject_id` (string, unique, deterministic subject identifier used in FHIR)
  - `display_name` (string, 1..200)
  - `subject_type` (enum: `human` | `veterinary`)
  - `created_at` (timestamp with timezone)
  - `updated_at` (timestamp with timezone)
- Validation rules:
  - `external_subject_id` required, immutable after creation
  - `display_name` required, trimmed
- Relationships:
  - 1:N with `LabReport`

## Entity: LabReport
- Fields:
  - `id` (UUID, PK)
  - `patient_id` (UUID, FK -> PatientProfile)
  - `original_filename` (string)
  - `mime_type` (must be `application/pdf`)
  - `file_hash_sha256` (string, indexed)
  - `pdf_storage_uri` (string)
  - `status` (enum: `uploaded` | `parsing` | `review_pending` | `editing` | `generating_bundle` | `regenerating_bundle` | `completed` | `failed` | `duplicate`)
  - `error_code` (nullable string)
  - `error_message` (nullable string)
  - `is_duplicate_of_report_id` (nullable UUID)
  - `created_at` / `updated_at` (timestamp with timezone)
- Validation rules:
  - Hash must be present before parsing starts
  - Scanned/image-based rejection sets `status=failed` with actionable error
- Relationships:
  - N:1 with `PatientProfile`
  - 1:N with `ParsedLabDataVersion`
  - 1:N with `FhirBundleArtifact`

## Entity: ParsedLabDataVersion
- Fields:
  - `id` (UUID, PK)
  - `report_id` (UUID, FK -> LabReport)
  - `version_number` (int, >=1)
  - `version_type` (enum: `original` | `corrected`)
  - `schema_version` (string)
  - `payload_json` (JSONB; intermediate schema contract)
  - `validation_status` (enum: `valid` | `invalid`)
  - `validation_errors` (JSONB nullable)
  - `created_by` (string; system/user id)
  - `created_at` (timestamp with timezone)
- Validation rules:
  - Exactly one `original` version per report
  - Latest `valid` version is source for bundle generation/regeneration
- Relationships:
  - N:1 with `LabReport`
  - 1:N with `EditHistoryEntry`

## Entity: LabMeasurement (logical, embedded in ParsedLabDataVersion payload)
- Fields:
  - `original_analyte_name` (string)
  - `normalized_analyte_code` (string; canonical)
  - `value_type` (enum: `numeric` | `qualitative` | `operator_numeric`)
  - `numeric_value` (nullable decimal)
  - `operator` (nullable enum: `<` | `<=` | `>` | `>=`)
  - `qualitative_value` (nullable string)
  - `original_unit` (nullable string)
  - `normalized_unit_ucum` (nullable string)
  - `reference_range_text` (nullable string)
  - `collection_datetime` (datetime)
  - `result_datetime` (nullable datetime)
- Validation rules:
  - Must contain either numeric/operator or qualitative value
  - `collection_datetime` required and must not be in the future

## Entity: FhirBundleArtifact
- Fields:
  - `id` (UUID, PK)
  - `report_id` (UUID, FK -> LabReport)
  - `parsed_version_id` (UUID, FK -> ParsedLabDataVersion)
  - `bundle_json` (JSONB)
  - `bundle_hash_sha256` (string)
  - `generated_at` (timestamp with timezone)
  - `generation_mode` (enum: `initial` | `regeneration`)
- Validation rules:
  - Bundle must be valid FHIR R4 transaction bundle
  - Must contain DocumentReference + DiagnosticReport + >=1 Observation
- Relationships:
  - N:1 with `LabReport`
  - N:1 with `ParsedLabDataVersion`
  - 1:N with `SubmissionRecord`

## Entity: SubmissionRecord (optional P5)
- Fields:
  - `id` (UUID, PK)
  - `bundle_artifact_id` (UUID, FK -> FhirBundleArtifact)
  - `target_base_url` (string)
  - `status` (enum: `pending` | `success` | `failed`)
  - `attempt_count` (int)
  - `last_error` (nullable string)
  - `submitted_at` (nullable timestamp with timezone)
  - `created_at` (timestamp with timezone)
- Validation rules:
  - `attempt_count >= 0`

## Entity: EditHistoryEntry
- Fields:
  - `id` (UUID, PK)
  - `parsed_version_id` (UUID, FK -> ParsedLabDataVersion)
  - `field_path` (string)
  - `old_value` (JSONB)
  - `new_value` (JSONB)
  - `edited_by` (string)
  - `edited_at` (timestamp with timezone)
- Validation rules:
  - Required for every user-initiated correction save

## State Transitions
- `uploaded -> parsing`
- `parsing -> review_pending` (valid intermediate schema)
- `parsing -> failed` (invalid PDF / extraction or schema failure)
- `review_pending -> editing` (user enters edit mode)
- `editing -> review_pending` (save valid edits)
- `review_pending -> generating_bundle` (user confirms)
- `generating_bundle -> completed` (bundle generated)
- `completed -> regenerating_bundle -> completed` (regenerate from stored parsed version)
- Any active state -> `failed` (terminal error)
- Duplicate upload path: `uploaded -> duplicate` with audit linkage

## FHIR Compatibility Check (R4)

### Compatibility status
- Compatible with required resource set: `Patient`, `DocumentReference`, `DiagnosticReport`, `Observation`, `Bundle` (transaction)
- Intermediate model supports required clinical timing at measurement level (`collection_datetime`, optional `result_datetime`)
- Source traceability is supported through persisted PDF metadata (`pdf_storage_uri`, `file_hash_sha256`, `original_filename`, `mime_type`)

### Discrepancies and resolution rules
- Discrepancy: FHIR requires resource statuses (`Observation.status`, `DiagnosticReport.status`, `DocumentReference.status`) and these are not explicit entity fields.
  - Resolution: Use deterministic defaults during projection: `Observation.status=final`, `DiagnosticReport.status=final`, `DocumentReference.status=current`, `DocumentReference.docStatus=final`.

- Discrepancy: Stable identifier systems are not explicitly documented in the model.
  - Resolution: Use fixed URN systems in projection:
    - Subject identifier system: `urn:lab2fhir:subject-id`
    - File hash identifier system: `urn:lab2fhir:file-sha256`
    - Local analyte coding system fallback: `urn:lab2fhir:analyte`
    - Report type coding system fallback: `urn:lab2fhir:report-type`

- Discrepancy: `normalized_analyte_code` does not include an explicit coding system.
  - Resolution: Infer system deterministically in projection:
    - If mapped to LOINC, use `http://loinc.org`
    - Else use local fallback `urn:lab2fhir:analyte`

- Discrepancy: Model has no explicit panel/report code for `DiagnosticReport.code`.
  - Resolution: Use deterministic fallback code when not extracted: `{system: urn:lab2fhir:report-type, code: LAB-PANEL, display: Laboratory report panel}`.

- Discrepancy: FHIR `DocumentReference.content.attachment.hash` is base64 of raw bytes, while stored hash is hex SHA-256.
  - Resolution: Convert stored hex SHA-256 to raw bytes then base64 at projection time.

## Data Model to FHIR Mapping

| Internal entity / field | FHIR resource.path | Mapping rule |
|---|---|---|
| `PatientProfile.external_subject_id` | `Patient.identifier[0].value` | Direct value |
| `PatientProfile.external_subject_id` | `Patient.identifier[0].system` | Constant `urn:lab2fhir:subject-id` |
| `PatientProfile.display_name` | `Patient.name[0].text` | Direct value |
| `PatientProfile.subject_type` | `Patient.extension(subject-type)` | `human`/`veterinary` value extension |
| `LabReport.id` | `DiagnosticReport.id` | Deterministic from report UUID |
| `LabReport.created_at` | `DocumentReference.date` | Direct value |
| `LabReport.mime_type` | `DocumentReference.content[0].attachment.contentType` | Direct value |
| `LabReport.original_filename` | `DocumentReference.content[0].attachment.title` | Direct value |
| `LabReport.pdf_storage_uri` | `DocumentReference.content[0].attachment.url` | Direct value |
| `LabReport.file_hash_sha256` | `DocumentReference.identifier[0].value` | Direct value |
| `LabReport.file_hash_sha256` | `DocumentReference.identifier[0].system` | Constant `urn:lab2fhir:file-sha256` |
| `LabReport.file_hash_sha256` | `DocumentReference.content[0].attachment.hash` | Hex SHA-256 -> raw bytes -> base64 |
| `LabMeasurement.collection_datetime` | `Observation.effectiveDateTime` | Direct value |
| `LabMeasurement.result_datetime` | `Observation.issued` | `result_datetime` else `collection_datetime` |
| `LabMeasurement.original_analyte_name` | `Observation.code.text` | Direct value |
| `LabMeasurement.normalized_analyte_code` | `Observation.code.coding[0].code` | Direct value |
| inferred analyte coding system | `Observation.code.coding[0].system` | `http://loinc.org` when mapped, else `urn:lab2fhir:analyte` |
| `LabMeasurement.value_type=numeric` + `numeric_value` | `Observation.valueQuantity.value` | Direct numeric |
| `LabMeasurement.value_type=operator_numeric` + `operator` | `Observation.valueQuantity.comparator` | Direct comparator |
| `LabMeasurement.value_type=qualitative` + `qualitative_value` | `Observation.valueString` | Direct string |
| `LabMeasurement.normalized_unit_ucum` | `Observation.valueQuantity.code` | UCUM code |
| `LabMeasurement.normalized_unit_ucum` | `Observation.valueQuantity.system` | Constant `http://unitsofmeasure.org` when UCUM is present |
| `LabMeasurement.original_unit` | `Observation.valueQuantity.unit` | Preserve display text |
| `LabMeasurement.reference_range_text` | `Observation.referenceRange[0].text` | Direct text |
| all observations for one report | `DiagnosticReport.result[]` | Stable sorted references to generated Observation IDs |
| report-level projection | `DiagnosticReport.subject` / `DocumentReference.subject` / `Observation.subject` | Reference same projected Patient |
| generated resources | `Bundle.type` | Constant `transaction` |
| generated resources | `Bundle.entry[*].request` | Deterministic `PUT {ResourceType}/{id}` for idempotent upserts |

### Deterministic ordering and IDs
- Bundle entry order is fixed: `Patient`, `DocumentReference`, `DiagnosticReport`, then `Observation[]` sorted by deterministic key.
- Observation deterministic ID seed remains: `{subject}|{collection_datetime}|{normalized_analyte}|{value}|{unit}`.
