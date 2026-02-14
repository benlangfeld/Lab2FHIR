# Lab2FHIR — Project Brief

## 1. Overview

**Lab2FHIR** is a self-hosted pipeline that converts structured laboratory PDF reports into FHIR-compliant clinical resources.

Its core purpose is to:

> Transform human- and veterinary lab reports in PDF form into validated FHIR `Observation`, `DiagnosticReport`, and `DocumentReference` resources.

The system is designed for:

- Personal / household health record management
- Multi-patient use (e.g., self, partner, pets)
- Long-term analytics integration
- Self-hosted infrastructure environments

Lab2FHIR acts as an ingestion layer between:

- Unstructured legacy lab PDFs
and
- A FHIR-based clinical data store (e.g., Fasten)

---

## 2. Problem Statement

Laboratory results are typically delivered as:

- Static PDFs
- Inconsistent formats
- Human-readable only
- Non-exportable structured data

Even modern labs often:

- Do not provide FHIR
- Do not provide CSV exports
- Provide inconsistent units
- Embed reference ranges visually only

This makes longitudinal tracking and analytics difficult.

There is currently:

- No lightweight open-source tool focused specifically on
  - personal-scale lab PDF → FHIR ingestion
  - multi-patient household use
  - integration with self-hosted FHIR stores

Lab2FHIR fills this gap.

---

## 3. Goals

### Primary Goals

1. Convert laboratory PDF reports into valid FHIR R4 Bundles
2. Support both human and veterinary lab reports
3. Operate fully self-hosted
4. Be infrastructure-light (minimal dependencies)
5. Be safe for PHI (no vendor lock-in required)

### Secondary Goals

- Provide deterministic deduplication
- Normalize units consistently
- Preserve original PDF as canonical document
- Enable later analytics (e.g., DuckDB, BI dashboards)
- Be extensible beyond lab reports

---

## 4. Non-Goals (Out of Scope)

- Acting as a full EHR
- Performing clinical decision support
- Automatically mapping to full LOINC terminology sets
- Real-time HL7 integration with hospitals
- Replacing wearable ingestion (handled separately via HealthKit export tools)

---

## 5. Constraints

### Infrastructure Constraints

- Designed to run on:
  - Heroku
  - VPS
  - NAS
  - Mac Mini
- Minimal additional services
- Postgres as primary persistence
- No dependency on enterprise FHIR SaaS products

### Data Constraints

- PDFs are primarily text-based (not scanned)
- Lab formats vary by provider
- Units may vary across time and labs
- Some analytes may be qualitative

### Privacy Constraints

- Must support PHI-safe operation
- LLM usage must be configurable
- Must allow future replacement of LLM component

---

## 6. System Architecture (High-Level)

```
PDF Upload
    ↓
Text Extraction (PDF parser)
    ↓
LLM Structured Parse (strict JSON schema)
    ↓
Validation + Normalization
    ↓
FHIR Bundle Generation
    ↓
FHIR Store (e.g., Fasten)
```

### Core Components

#### 1. Ingestion Layer
- Accepts PDF uploads
- Routes to subject (patient)
- Deduplicates by file hash

#### 2. Parsing Layer
- Extracts text from PDF
- Uses LLM with strict schema to produce structured intermediate JSON
- No direct FHIR generation from model

#### 3. Normalization Layer
- Canonicalizes:
  - Units
  - Dates
  - Analyte names
- Validates numeric vs qualitative values
- Enforces internal consistency

#### 4. FHIR Generation Layer
Generates:

- `DocumentReference`
- `DiagnosticReport`
- `Observation[]`
- Optional `Provenance`

Emits a transaction `Bundle`

#### 5. Import Layer
- POSTs Bundle to FHIR server
- Records status
- Handles retry + failure tracking

---

## 7. Data Model Strategy

### Intermediate JSON Model (LLM Output Contract)

The LLM must output a strict schema that includes:

- Lab metadata
- Collection date
- Result list
  - Name
  - Value (numeric or text)
  - Unit
  - Reference range

This intermediate model:

- Is validated before FHIR conversion
- Serves as audit log
- Decouples LLM from FHIR implementation

---

## 8. FHIR Strategy

### Minimal FHIR Resources

- `Observation` — each analyte
- `DiagnosticReport` — lab panel
- `DocumentReference` — original PDF
- `Bundle` (transaction) — atomic ingestion

### Deduplication Strategy

Each Observation includes a deterministic identifier:

```
{subject}|{collection_date}|{normalized_analyte}|{value}|{unit}
```

Prevents duplicate import on reprocessing.

---

## 9. Design Principles

1. Deterministic > Clever
2. Validated JSON > Freeform text
3. Intermediate model > Direct FHIR from LLM
4. Store original PDF always
5. Keep infrastructure minimal
6. Avoid vendor lock-in

---

## 10. Landscape Analysis

### Existing Options

| Tool | Issue |
|------|-------|
| Enterprise OCR-to-FHIR | Expensive |
| Aidbox Forms | Commercial, PHI-restricted |
| Full EHR platforms | Overkill |
| Manual CSV imports | Not scalable |
| Custom regex parsing | Brittle |

There is no lightweight, OSS-focused, household-scale PDF → FHIR tool.

Lab2FHIR positions itself as:

> A focused ingestion microservice for lab reports.

---

## 11. Future Extensions

- LOINC code mapping layer
- Unit conversion engine
- Local LLM support
- Dashboard-friendly export
- CLI ingestion mode
- S3 attachment mode
- Veterinary-specific schema extensions
- Analytics-friendly Parquet export

---

## 12. Success Criteria

Lab2FHIR is successful if:

- A lab PDF can be uploaded
- Observations appear correctly in Fasten
- Duplicate uploads do not create duplicate labs
- Units are consistent over time
- Multi-patient separation works cleanly
- It runs reliably on a small server

---

## 13. Guiding Philosophy

Lab2FHIR is not an EHR.

It is:

> A deterministic ingestion pipeline that transforms legacy clinical documents into structured, interoperable health data.
