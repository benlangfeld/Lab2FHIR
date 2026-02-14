# Feature Specification: Lab PDF to FHIR Converter

**Feature Branch**: `001-lab-pdf-fhir-converter`
**Created**: 2026-02-14
**Status**: Draft
**Input**: User description: "Build a self-hosted pipeline that converts structured laboratory PDF reports into FHIR-compliant clinical resources for personal and household health record management"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload and Process Single Lab Report (Priority: P1)

A household health manager uploads a PDF lab report from their personal medical records via the web interface and receives the structured data in their FHIR store within minutes, enabling them to track health trends over time.

**Why this priority**: This is the core value proposition - converting a single lab PDF into FHIR resources. Without this, the system provides no value. This represents the minimal viable product.

**Independent Test**: Can be fully tested by uploading a single lab PDF file through the web interface, verifying the system extracts and structures the data, generates valid FHIR resources (Observation, DiagnosticReport, DocumentReference), and successfully stores them. Success is confirmed by querying the FHIR store and seeing the lab results as structured observations.

**Acceptance Scenarios**:

1. **Given** a household manager has a lab PDF report and an existing patient profile, **When** they upload the PDF through the web interface and select the patient, **Then** the system extracts text, parses lab results using structured LLM prompting, validates against the intermediate JSON schema, and generates a FHIR Bundle
2. **Given** a valid FHIR Bundle has been generated, **When** the system submits it to the configured FHIR store, **Then** the data appears as queryable Observations linked to a DiagnosticReport with the original PDF preserved as a DocumentReference
3. **Given** a successfully processed lab report, **When** the user views the processing status in the web interface, **Then** they see "Completed" status with a confirmation that data was imported to the FHIR store
4. **Given** a successfully processed lab report, **When** the user queries their FHIR store, **Then** they can retrieve specific analyte values (e.g., "show me all glucose readings") with correct units and dates

---

### User Story 2 - Handle Multiple Patients (Priority: P2)

A household with multiple people (partner, children) and pets creates patient profiles for each member, then uploads lab reports for different subjects and can distinguish between each person's or pet's results in their consolidated health records.

**Why this priority**: Multi-patient support is essential for household-scale usage but can be tested after basic single-report processing works. This expands the system's utility without changing core processing logic.

**Independent Test**: Can be tested by first creating 2-3 patient profiles through the web interface (e.g., "John Doe" [human], "Jane Doe" [human], "Fluffy the Cat" [veterinary]), then uploading lab reports for each, and verifying that each report's FHIR resources correctly reference the appropriate Patient resource, and that querying results by patient returns only that patient's data.

**Acceptance Scenarios**:

1. **Given** no patient profiles exist, **When** a user creates a new patient profile via the web interface specifying name and type (human/veterinary), **Then** the system generates a unique patient identifier and stores the profile
2. **Given** multiple patient profiles exist, **When** a user uploads a lab report, **Then** the web interface displays a dropdown to select the appropriate patient profile
3. **Given** lab reports exist for multiple household members, **When** a report is uploaded for a specific patient, **Then** the system correctly associates the lab results with the selected patient identifier in the generated FHIR resources
4. **Given** lab reports for both humans and pets, **When** reports are processed, **Then** veterinary lab reports are handled correctly with appropriate subject references
5. **Given** multiple patients in the system, **When** querying the FHIR store for one patient's lab results, **Then** only that patient's observations are returned

---

### User Story 3 - Prevent Duplicate Imports (Priority: P2)

A user accidentally uploads the same lab report PDF twice and the system recognizes the duplicate, preventing redundant data entries in the FHIR store while still preserving both upload attempts for audit purposes.

**Why this priority**: Duplicate prevention is critical for data integrity and prevents database bloat, but the system can function without it initially. Users can work around by manually managing uploads.

**Independent Test**: Can be tested by uploading the same PDF file twice and verifying that: (1) the file hash is detected as a duplicate, (2) no duplicate FHIR Observations are created, (3) the system logs the duplicate attempt, and (4) querying the FHIR store shows only one set of observations for that collection date.

**Acceptance Scenarios**:

1. **Given** a lab PDF has been previously uploaded, **When** the exact same file is uploaded again, **Then** the system detects the duplicate by file hash and prevents reprocessing
2. **Given** the same lab data from different PDF files (e.g., downloaded twice from portal), **When** both are uploaded, **Then** the system uses deterministic identifiers to prevent duplicate Observations from being created
3. **Given** a reprocessing attempt of a previously failed upload, **When** the corrected file is uploaded, **Then** the system allows reprocessing while maintaining data integrity

---

### User Story 4 - Normalize Units Across Time (Priority: P3)

A user uploads lab reports from different labs taken over several years with varying unit systems (mg/dL vs mmol/L) and the system normalizes units to consistent standards, enabling accurate longitudinal comparisons.

**Why this priority**: Unit normalization significantly improves data utility for analytics but isn't required for basic functionality. Users can manually interpret different units initially.

**Independent Test**: Can be tested by uploading lab reports with the same analyte measured in different units (e.g., glucose in mg/dL and mmol/L) and verifying that the system either normalizes to a canonical unit or preserves both the original and normalized values, allowing queries to compare values across time periods.

**Acceptance Scenarios**:

1. **Given** lab reports with glucose measured in mg/dL and mmol/L, **When** both are processed, **Then** the system standardizes units to enable direct comparison
2. **Given** inconsistent analyte naming across labs (e.g., "Hemoglobin" vs "HGB" vs "Hb"), **When** reports are processed, **Then** the system normalizes analyte names for consistent querying
3. **Given** normalized units have been applied, **When** users query historical trends, **Then** all values use consistent units for accurate comparison

---

### User Story 5 - Preserve Original Documents (Priority: P3)

A user needs to verify original lab results or share the official report with a healthcare provider and can retrieve the original PDF document that was uploaded, linked to all derived FHIR resources.

**Why this priority**: Source preservation is important for trust and legal requirements but doesn't block initial functionality. The core value is in structured data extraction.

**Independent Test**: Can be tested by uploading a PDF, processing it into FHIR resources, then retrieving the original PDF via the DocumentReference resource and verifying it matches the uploaded file exactly (byte-for-byte identical).

**Acceptance Scenarios**:

1. **Given** a lab report has been processed, **When** querying the DiagnosticReport, **Then** it includes a reference to a DocumentReference containing the original PDF
2. **Given** a DocumentReference exists, **When** retrieving the PDF, **Then** the document is byte-identical to the original upload
3. **Given** FHIR Observations exist, **When** tracing provenance, **Then** each Observation links back to the source DocumentReference for audit purposes

---

### Edge Cases

- What happens when a PDF contains no recognizable lab data (e.g., wrong document type)? System should reject with clear error message.
- What happens when a PDF contains mixed content (lab results plus clinical notes)? System should extract only the lab results portion.
- What happens when numeric values include qualitative indicators (e.g., "<5.0" or ">1000")? System should preserve both operator and value.
- What happens when reference ranges vary by demographics (age/gender)? System should preserve the specific reference range stated in the report.
- What happens when analyte names contain special characters or are abbreviated differently? System should handle variations and preserve original naming.
- What happens when collection date is missing or ambiguous? System should flag for manual review.
- What happens when the PDF is scanned/image-based rather than text-based? System should detect and reject with appropriate error message (out of scope for text-based parsing).
- What happens when submission to FHIR store fails (network error, server down)? System should queue for retry and track failure status.
- What happens when the same lab analyte appears multiple times in one report (e.g., redraws)? System should preserve all instances with appropriate sequencing.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Ingestion

- **FR-001**: System MUST accept PDF file uploads and route them to the appropriate patient/subject
- **FR-001a**: System MUST provide a web-based upload interface as the primary interaction method, allowing users to select PDF files and specify the associated patient identifier
- **FR-002**: System MUST extract text content from text-based PDF files
- **FR-003**: System MUST detect and reject image-based/scanned PDFs with a clear error message
- **FR-004**: System MUST calculate and store file hash for each uploaded PDF to enable deduplication
- **FR-005**: System MUST prevent duplicate processing when the same file hash is encountered

#### Parsing and Extraction

- **FR-006**: System MUST extract structured lab data including: analyte names, numeric or qualitative values, units of measurement, reference ranges, collection date, and lab metadata
- **FR-006a**: System MUST use structured prompting with JSON schema enforcement (via function calling or constrained generation) to ensure LLM outputs strictly conform to the intermediate schema, eliminating post-hoc validation failures
- **FR-007**: System MUST use a validated intermediate JSON schema as the contract between parsing and FHIR generation
- **FR-008**: System MUST validate extracted data against the intermediate schema before FHIR conversion
- **FR-009**: System MUST handle qualitative values (e.g., "Positive", "Negative") and numeric values with operators (e.g., "<5.0", ">1000")
- **FR-010**: System MUST preserve original analyte names and units as stated in the source document

#### Normalization

- **FR-011**: System MUST normalize date formats to a canonical representation
- **FR-012**: System MUST normalize analyte names to enable consistent querying across different lab providers
- **FR-013**: System MUST normalize units to standard representations where appropriate
- **FR-014**: System MUST preserve both original and normalized values for traceability

#### FHIR Resource Generation

- **FR-015**: System MUST generate valid FHIR R4 Bundle resources containing all converted lab data
- **FR-016**: System MUST create a DocumentReference resource for each uploaded PDF
- **FR-017**: System MUST create a DiagnosticReport resource representing the lab panel
- **FR-018**: System MUST create individual Observation resources for each analyte measurement
- **FR-019**: System MUST link Observations to their parent DiagnosticReport
- **FR-020**: System MUST link the DiagnosticReport to the source DocumentReference
- **FR-021**: System MUST generate deterministic identifiers for each Observation using the pattern: {subject}|{collection_date}|{normalized_analyte}|{value}|{unit}
- **FR-022**: System MUST use transaction Bundles to ensure atomic submission of all resources

#### Multi-Patient Support

- **FR-023**: System MUST support associating lab reports with multiple distinct patient/subject identifiers
- **FR-023a**: System MUST allow users to create and manage patient profiles (including name, type: human/veterinary, and unique identifier) through the web interface before uploading lab reports
- **FR-023b**: System MUST allow users to select from existing patient profiles when uploading a lab report
- **FR-024**: System MUST support both human and veterinary patient subjects
- **FR-025**: System MUST maintain clear separation of data between different patients/subjects

#### FHIR Store Integration

- **FR-026**: System MUST submit generated Bundles to a configured FHIR server endpoint
- **FR-026a**: System MUST support configuration of FHIR server connection details (base URL, authentication method) via environment variables or configuration file
- **FR-026b**: System MUST support FHIR R4-compliant servers (including Fasten, HAPI FHIR, and other standards-compliant implementations)
- **FR-026c**: System MUST support both unauthenticated and basic authentication for FHIR server connections
- **FR-027**: System MUST record submission status (success, pending, failed) for each processed report
- **FR-028**: System MUST implement retry logic for failed submissions
- **FR-029**: System MUST track and log all submission attempts for audit purposes

#### Data Integrity

- **FR-030**: System MUST validate that extracted collection dates are reasonable (not future dates)
- **FR-031**: System MUST validate that numeric values are within reasonable ranges for their analyte type
- **FR-032**: System MUST flag reports with missing critical data (e.g., collection date) for manual review
- **FR-033**: System MUST preserve the original PDF file for the lifetime of the associated FHIR resources

#### Privacy and Security

- **FR-034**: System MUST operate entirely within a self-hosted environment without requiring external SaaS services
- **FR-035**: System MUST allow configuration of LLM usage (local vs. API-based) to meet PHI requirements
- **FR-036**: System MUST handle Protected Health Information (PHI) in compliance with data protection requirements

#### User Feedback and Error Handling

- **FR-037**: System MUST provide immediate feedback to users upon PDF upload, indicating whether the upload was successful or failed
- **FR-038**: System MUST display processing status (queued, processing, completed, failed) for each uploaded report in the web interface
- **FR-039**: System MUST provide clear, actionable error messages when processing fails, indicating the reason (e.g., "PDF is scanned/image-based", "Missing collection date", "Invalid file format")
- **FR-040**: System MUST allow users to view the processing history and status of all previously uploaded reports
- **FR-041**: System MUST notify users when a report is successfully imported to the FHIR store, with a link or reference to view the data

### Key Entities

- **Lab Report**: Represents an uploaded PDF document containing laboratory test results. Key attributes: file hash, upload timestamp, associated patient, processing status (queued, processing, completed, failed), error messages (if any), source file reference.

- **Parsed Lab Data**: Intermediate structured representation of lab results extracted from PDF using structured LLM prompting with JSON schema enforcement. Key attributes: lab metadata (name, address), collection date, report date, result list (each with analyte name, value, unit, reference range). This is the validated JSON contract between parsing and FHIR generation.

- **Patient/Subject Profile**: Represents the individual (human or animal) to whom the lab results belong. Key attributes: patient identifier (system-generated or user-provided), display name, patient type (human/veterinary), creation date. Relationships: has many lab reports, has many observations. Managed through web interface.

- **Lab Analyte Measurement**: Individual test result within a lab report. Key attributes: analyte name (original and normalized), value (numeric or qualitative), unit (original and normalized), reference range, collection timestamp. Relationships: belongs to lab report, maps to FHIR Observation.

- **FHIR Bundle**: Transaction bundle containing all FHIR resources for a single lab report. Relationships: contains DocumentReference, DiagnosticReport, and multiple Observation resources.

- **Submission Record**: Tracks the status of FHIR Bundle submission to the target FHIR server. Key attributes: submission timestamp, status (pending/success/failed), retry count, error messages, FHIR server endpoint used. Relationships: associated with one FHIR Bundle.

- **System Configuration**: Stores system-wide settings. Key attributes: FHIR server base URL, authentication credentials, LLM provider settings (local vs. API-based), retry policy parameters. Managed via environment variables or configuration file.

- **Lab Analyte Measurement**: Individual test result within a lab report. Key attributes: analyte name (original and normalized), value (numeric or qualitative), unit (original and normalized), reference range, collection timestamp. Relationships: belongs to lab report, maps to FHIR Observation.

- **FHIR Bundle**: Transaction bundle containing all FHIR resources for a single lab report. Relationships: contains DocumentReference, DiagnosticReport, and multiple Observation resources.

- **Submission Record**: Tracks the status of FHIR Bundle submission to the target FHIR server. Key attributes: submission timestamp, status (pending/success/failed), retry count, error messages. Relationships: associated with one FHIR Bundle.

## Constitution Alignment *(mandatory)*

- **Deterministic Behavior**: The system ensures deterministic outputs through:
  - File hash-based deduplication prevents duplicate processing of identical uploads
  - Deterministic FHIR Observation identifiers using the pattern {subject}|{collection_date}|{normalized_analyte}|{value}|{unit} prevent duplicate observations even if the same data is processed multiple times
  - Normalization rules (date formats, analyte names, units) follow consistent, reproducible transformations
  - FHIR Bundle generation follows a fixed structure and ordering
  - Reprocessing the same source data will always produce identical FHIR resources

- **Intermediate Schema Contract**: The system strictly enforces the intermediate JSON schema:
  - LLM parsing outputs to a validated JSON schema, not directly to FHIR
  - The intermediate schema includes: lab metadata, collection date, result list with structured fields (name, value, unit, reference range)
  - Schema validation occurs before any FHIR conversion begins
  - This decouples LLM behavior from FHIR implementation, allowing either component to evolve independently
  - Direct model-to-FHIR generation is explicitly prohibited
  - The intermediate JSON serves as an audit log and testing boundary

- **Source Traceability**: The system maintains complete source traceability:
  - Every uploaded PDF is preserved as a FHIR DocumentReference resource with the original file content
  - Every DiagnosticReport links to its source DocumentReference
  - Every Observation references its parent DiagnosticReport, creating a traceable chain to the original PDF
  - File hash is recorded for deduplication and verification purposes
  - Processing timestamps and status records enable audit trails
  - Users can always retrieve the original PDF to verify against structured data

- **PHI & Hosting Constraints**: The system respects PHI and self-hosting requirements:
  - All components operate within a self-hosted environment (Heroku, VPS, NAS, Mac Mini)
  - No mandatory external SaaS dependencies for core functionality
  - LLM usage is configurable - supports both API-based and local LLM options
  - Users maintain full control over where PHI is stored and processed
  - The system is designed for lightweight deployment with minimal infrastructure dependencies
  - FHIR store integration is configuration-driven, not hard-coded to specific vendors
  - Database selection (Postgres recommended) is deployment-specific, not architecturally mandated

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A household user can successfully upload a lab PDF via the web interface and see structured results in their FHIR store within 5 minutes of upload
- **SC-002**: System correctly extracts and structures at least 95% of lab analytes from standard text-based lab reports using structured LLM prompting
- **SC-003**: Duplicate uploads of the same PDF are detected and prevented 100% of the time via file hash comparison
- **SC-004**: Generated FHIR resources pass validation against FHIR R4 specification 100% of the time
- **SC-005**: System successfully handles lab reports for at least 3 different patients/subjects with complete data separation
- **SC-006**: Units are normalized consistently - querying for the same analyte across multiple reports returns comparable values 90%+ of the time
- **SC-007**: Every processed lab report maintains a verifiable link from Observation → DiagnosticReport → DocumentReference → original PDF
- **SC-008**: System operates successfully on a small server (2GB RAM, 2 CPU cores) with response time under 2 minutes per report
- **SC-009**: Failed FHIR submissions are automatically retried with 95%+ eventual success rate for transient failures
- **SC-010**: 90% of users can successfully complete their first lab upload without documentation or support assistance
- **SC-011**: Users can create a patient profile and upload their first lab report within 3 minutes using the web interface
- **SC-012**: Processing status updates are visible in the web interface within 5 seconds of status changes
- **SC-013**: Error messages clearly indicate the cause of failure in 95%+ of error scenarios, enabling users to take corrective action
