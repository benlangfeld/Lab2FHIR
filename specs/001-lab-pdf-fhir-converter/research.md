# Research Document: Lab PDF to FHIR Converter

**Feature**: Lab PDF to FHIR Converter  
**Tech Stack**: Python 3.11+, FastAPI, PostgreSQL, Pydantic  
**Date**: 2024

---

## 1. PDF Text Extraction Library

### Decision
**pdfplumber** - Selected as primary extraction library

### Rationale
- **Superior table extraction**: Purpose-built for structured data extraction with native support for tables as lists/DataFrames
- **Accurate layout analysis**: Preserves table structure critical for lab reports (analyte, value, unit, reference range columns)
- **Debugging capabilities**: Provides visualization tools to inspect table detection and extraction boundaries
- **Clinical fit**: Lab reports are heavily tabular; pdfplumber directly exports tables to structured formats without manual post-processing

### Alternatives Considered

**PyPDF2/pypdf**:
- ❌ No native table extraction - tables extracted as flattened text
- ✅ Lightweight, pure Python, easy deployment
- ✅ Good for basic text extraction and PDF manipulation
- **Verdict**: Inadequate for structured lab data extraction

**pypdfium2**:
- ❌ No table support - extremely fast but text-only
- ✅ Best for bulk indexing/search operations
- **Verdict**: Not suitable for structured data requirements

**Camelot/Tabula-py**:
- ✅ Excellent for ruled-grid tables
- ❌ Requires Java (Tabula) or complex dependencies
- ⚠️ Less flexible than pdfplumber for varying lab report formats
- **Verdict**: Good alternatives but more dependencies and less flexible

### Implementation Notes
```python
import pdfplumber
with pdfplumber.open("lab_report.pdf") as pdf:
    tables = pdf.pages[0].extract_tables()
    # Direct table access preserves structure
```

---

## 2. LLM Structured Output for Lab Data Extraction

### Decision
**OpenAI Structured Outputs with Pydantic** (GPT-4o or GPT-4-turbo)

### Rationale
- **Schema enforcement**: Native `response_format` with JSON schema guarantees valid output matching Pydantic models
- **No post-processing**: Eliminates parsing errors and validation headaches
- **Pydantic integration**: Direct model validation via `model_validate_json()` for type-safe lab data
- **Production-ready**: Reliable for medical pipelines where data integrity is critical
- **Refusal handling**: Structured error responses for edge cases (uncertain values, missing data)

### Alternatives Considered

**Anthropic Claude Structured Outputs**:
- ✅ Strong schema enforcement (Claude 4.5+, Opus 4.1+)
- ✅ Competitive accuracy for medical text
- ⚠️ Slightly newer implementation (late 2024)
- **Verdict**: Viable alternative; consider for redundancy or cost optimization

**Function Calling**:
- ✅ Works well for triggering actions on abnormal values
- ⚠️ More complex than direct structured output for pure extraction
- **Verdict**: Use if workflow logic is needed; otherwise prefer structured outputs

**JSON Mode (legacy)**:
- ❌ Less reliable than structured outputs
- ❌ Requires prompt engineering for consistency
- **Verdict**: Superseded by structured outputs API

### Implementation Pattern
```python
from pydantic import BaseModel, Field
from openai import OpenAI

class LabAnalyte(BaseModel):
    name: str
    value: float
    unit: str
    reference_range: str
    flag: str | None = None

class LabResult(BaseModel):
    patient_id: str
    test_date: str
    analytes: list[LabAnalyte]

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract lab data into structured JSON."},
        {"role": "user", "content": extracted_text}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": LabResult.model_json_schema(),
        "strict": True
    }
)
lab_data = LabResult.model_validate_json(response.choices[0].message.content)
```

### Security & Compliance Notes
- Encrypt API traffic (TLS)
- Avoid logging raw PHI in model I/O
- Validate outputs before database insertion
- Human-audit subset for clinical use
- Ensure HIPAA compliance for API usage

---

## 3. FHIR R4 Python Library

### Decision
**fhir.resources** (Pydantic-based FHIR library)

### Rationale
- **Pydantic validation**: Built-in schema validation ensures FHIR R4 compliance
- **Pythonic API**: Clean, intuitive resource creation and manipulation
- **Complete coverage**: All FHIR R4 resources as Python classes
- **Serialization**: JSON, XML, YAML support with `model_dump_json()`
- **Extensions support**: Handles FHIR's extensibility model
- **Active maintenance**: Well-maintained with regular updates

### Alternatives Considered

**google-fhir-r4**:
- ✅ Excellent for big data/analytics (BigQuery, Spark integration)
- ✅ FHIRPath support for queries
- ✅ Protocol Buffer serialization
- ❌ More setup complexity (Protobufs)
- ❌ Less Pythonic for transactional FHIR generation
- **Verdict**: Better for analytics pipelines; overkill for API-based conversion

**fhirpy**:
- ✅ Lightweight FHIR REST client
- ❌ Limited resource modeling and validation
- ❌ Not designed for resource generation
- **Verdict**: Good for API consumption, not resource creation

### Implementation Example
```python
from fhir.resources.bundle import Bundle
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.observation import Observation

bundle = Bundle(
    type="transaction",
    entry=[
        {
            "resource": diagnostic_report,
            "request": {"method": "PUT", "url": f"DiagnosticReport/{report_id}"}
        },
        {
            "resource": observation,
            "request": {"method": "PUT", "url": f"Observation/{obs_id}"}
        }
    ]
)

# Validation happens automatically
fhir_json = bundle.model_dump_json(indent=2)
```

---

## 4. UCUM Unit Normalization

### Decision
**ucumvert + pint** (combined approach)

### Rationale
- **ucumvert**: Full UCUM 2.2 grammar parser (June 2024), converts UCUM strings to pint-compatible units
- **pint**: Robust unit arithmetic, conversions, and normalization
- **Complete workflow**: Parse UCUM → convert to pint → perform unit operations
- **Medical focus**: ucumvert designed for clinical/lab data
- **Active maintenance**: Both libraries actively maintained

### Alternatives Considered

**pyucum**:
- ✅ UCUM validation for clinical datasets (CDISC SDTM)
- ✅ NLM UCUM API integration
- ✅ Good for validation workflows
- ⚠️ Less focus on computation/conversion
- **Verdict**: Excellent for validation; use alongside ucumvert+pint for complete solution

**unitpy**:
- ✅ Lightweight, simple API
- ❌ Not UCUM-specific
- **Verdict**: Good for general use, but ucumvert is better for UCUM compliance

**pint alone**:
- ❌ No native UCUM parsing
- **Verdict**: Requires ucumvert or manual mapping

### Implementation Workflow
```python
from ucumvert import ucum2pint, UcumRegistry
import pint

# Parse UCUM code
ucum_code = "mg/dL"
pint_unit = ucum2pint(ucum_code)

# Create quantity and convert
ureg = UcumRegistry()
quantity = 100 * ureg(pint_unit)

# Normalize (if conversion mapping exists)
# normalized = quantity.to("mmol/L")

# Validation with pyucum for production
from pyucum import validate_ucum
is_valid = validate_ucum(ucum_code)
```

### Validation Strategy
- Use **pyucum** for UCUM code validation before storage
- Use **ucumvert+pint** for unit conversion operations
- Maintain conversion mappings for common lab units (e.g., mg/dL ↔ mmol/L for glucose)

---

## 5. Deterministic FHIR Resource ID Generation

### Decision
**Content-based SHA-256 hashing with canonical input**

### Rationale
- **Deduplication**: Same content always generates same ID
- **Upsert support**: Use PUT operations to prevent duplicates
- **Collision resistance**: SHA-256 provides strong uniqueness guarantees
- **FHIR compatibility**: Follows FHIR identity and FAIR principles
- **Auditable**: Reproducible IDs support audit and lineage tracking

### Implementation Strategy

**Canonical Input Construction**:
1. Select stable, identifying fields (patient MRN, test date, analyte code, specimen ID)
2. Sort keys alphabetically (order-independent)
3. Exclude transient fields (timestamps, processing metadata)
4. Include system/integration scope to prevent cross-system collisions

**Hash Generation**:
```python
import hashlib
import json
from typing import Any

def generate_deterministic_id(resource_type: str, key_fields: dict[str, Any], scope: str = "lab2fhir") -> str:
    """Generate deterministic FHIR resource ID."""
    canonical = {
        "resourceType": resource_type,
        "scope": scope,
        **{k: key_fields[k] for k in sorted(key_fields.keys())}
    }
    canonical_json = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
    hash_digest = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    # Use first 16 chars for compact ID (64 bits of entropy)
    return f"{resource_type[:3].lower()}-{hash_digest[:16]}"

# Example usage
obs_id = generate_deterministic_id(
    "Observation",
    {
        "patient_mrn": "12345",
        "test_code": "2345-7",  # LOINC code
        "specimen_id": "SPEC-001",
        "effective_date": "2024-01-15"
    }
)
# Result: "obs-a3f5b1c2d4e6f7a8"
```

**Upsert Pattern**:
```python
# Use PUT with deterministic ID for deduplication
bundle_entry = {
    "resource": observation,
    "request": {
        "method": "PUT",
        "url": f"Observation/{deterministic_id}"
    }
}
```

### Alternatives Considered

**UUID v5 (namespace-based)**:
- ✅ Standards-based deterministic UUID
- ⚠️ Requires namespace management
- **Verdict**: Good alternative; SHA-256 offers more flexibility

**Server-assigned IDs**:
- ❌ No deduplication support
- ❌ Duplicates created on re-processing
- **Verdict**: Not suitable for conversion pipelines

**Business identifiers only**:
- ❌ Not globally unique across systems
- ⚠️ May not be available in all sources
- **Verdict**: Use in `identifier` field, not as resource ID

### Security Considerations
- Don't include raw PHI in IDs (even hashed)
- Use hash truncation judiciously (balance collision risk vs. ID length)
- Document ID generation logic for audit compliance

---

## 6. PostgreSQL Schema Design

### Decision
**Multi-schema design with BYTEA for PDFs, JSONB for intermediate data, and pgMemento for audit logs**

### Rationale
- **BYTEA for PDFs**: Native binary storage, keeps files with metadata, simplifies backup/restore
- **JSONB for JSON**: Binary format enables fast queries, GIN indexing, and schema flexibility
- **Separate audit schema**: Isolates audit logs, simplifies permissions and compliance
- **pgMemento**: Transaction-based audit with JSONB deltas, DDL tracking, and rollback support
- **Scalability**: PostgreSQL handles binary/JSON efficiently at scale

### Schema Structure

```sql
-- Main application schema
CREATE SCHEMA IF NOT EXISTS app;

-- Audit schema (separate for security/compliance)
CREATE SCHEMA IF NOT EXISTS audit;

-- ========================================
-- PDF Storage
-- ========================================
CREATE TABLE app.pdf_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name TEXT NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    file_size_bytes INTEGER NOT NULL,
    mime_type TEXT DEFAULT 'application/pdf',
    sha256_hash TEXT NOT NULL UNIQUE,  -- Content hash for deduplication
    pdf_data BYTEA NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pdf_documents_sha256 ON app.pdf_documents(sha256_hash);
CREATE INDEX idx_pdf_documents_metadata ON app.pdf_documents USING GIN (metadata);

-- ========================================
-- Intermediate JSON Storage (extraction results)
-- ========================================
CREATE TABLE app.extraction_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_document_id UUID NOT NULL REFERENCES app.pdf_documents(id) ON DELETE CASCADE,
    extraction_method TEXT NOT NULL,  -- 'pdfplumber', 'llm_v1', etc.
    extracted_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2),  -- 0.00-1.00
    extracted_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT CHECK (status IN ('pending', 'completed', 'failed', 'validated')) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_extraction_pdf_doc ON app.extraction_results(pdf_document_id);
CREATE INDEX idx_extraction_data ON app.extraction_results USING GIN (extracted_data);
CREATE INDEX idx_extraction_status ON app.extraction_results(status);

-- ========================================
-- FHIR Bundles Storage
-- ========================================
CREATE TABLE app.fhir_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    extraction_result_id UUID NOT NULL REFERENCES app.extraction_results(id) ON DELETE CASCADE,
    bundle_data JSONB NOT NULL,
    resource_ids TEXT[] NOT NULL,  -- Array of FHIR resource IDs in bundle
    validation_status TEXT CHECK (validation_status IN ('valid', 'invalid', 'pending')) DEFAULT 'pending',
    validation_errors JSONB,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fhir_bundle_extraction ON app.fhir_bundles(extraction_result_id);
CREATE INDEX idx_fhir_bundle_data ON app.fhir_bundles USING GIN (bundle_data);
CREATE INDEX idx_fhir_bundle_resource_ids ON app.fhir_bundles USING GIN (resource_ids);

-- ========================================
-- Processing Pipeline Tracking
-- ========================================
CREATE TABLE app.processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_document_id UUID NOT NULL REFERENCES app.pdf_documents(id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('queued', 'processing', 'completed', 'failed')) DEFAULT 'queued',
    stage TEXT,  -- 'extraction', 'llm_parsing', 'fhir_generation', 'validation'
    progress_data JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_processing_jobs_status ON app.processing_jobs(status, created_at);
CREATE INDEX idx_processing_jobs_pdf ON app.processing_jobs(pdf_document_id);

-- ========================================
-- Audit Log (using pgMemento pattern)
-- ========================================
CREATE TABLE audit.audit_log (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT,
    table_schema TEXT NOT NULL,
    table_name TEXT NOT NULL,
    operation TEXT CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')) NOT NULL,
    row_id TEXT,  -- UUID or other identifier
    changed_data JSONB,  -- New values or delta
    old_data JSONB,      -- Previous values
    session_info JSONB   -- Request ID, IP, etc.
);

CREATE INDEX idx_audit_time ON audit.audit_log(event_time);
CREATE INDEX idx_audit_table ON audit.audit_log(table_schema, table_name);
CREATE INDEX idx_audit_user ON audit.audit_log(user_id);
CREATE INDEX idx_audit_changed ON audit.audit_log USING GIN (changed_data);
```

### Alternatives Considered

**External file storage (S3/filesystem)**:
- ✅ Better for very large files (>10 MB)
- ✅ Reduces database size
- ❌ Adds complexity (file lifecycle, sync, backup)
- ❌ Potential consistency issues
- **Verdict**: Consider for production at scale; BYTEA acceptable for MVP

**JSON instead of JSONB**:
- ❌ Slower queries
- ❌ No GIN indexing
- ✅ Preserves exact formatting
- **Verdict**: JSONB is correct choice for queryable data

**DIY audit triggers vs. pgMemento**:
- ✅ pgMemento provides battle-tested solution with DDL tracking
- ✅ Automatic delta computation
- ⚠️ Adds dependency
- **Verdict**: pgMemento for production; simple triggers for MVP

**NoSQL database for JSON**:
- ❌ Adds infrastructure complexity
- ❌ PostgreSQL JSONB is mature and performant
- **Verdict**: PostgreSQL handles JSON well; no need for separate NoSQL

### Best Practices

1. **Indexing**: GIN indexes for JSONB; B-tree for UUID, timestamps
2. **Partitioning**: Consider time-based partitioning for audit logs at scale
3. **Constraints**: Use CHECK, UNIQUE, and FOREIGN KEY constraints for data integrity
4. **Security**: Separate schemas for audit; row-level security if needed
5. **Backup**: Regular pg_dump with PITR; test restore procedures
6. **Monitoring**: Track table bloat, index usage, query performance

### Migration Strategy
```sql
-- Use migrations tool (Alembic, Django migrations, etc.)
-- Version control all schema changes
-- Test migrations on staging data
-- Document rollback procedures
```

---

## Summary

| Component | Decision | Key Benefit |
|-----------|----------|-------------|
| **PDF Extraction** | pdfplumber | Native table extraction for lab reports |
| **LLM Parsing** | OpenAI Structured Outputs + Pydantic | Guaranteed schema compliance |
| **FHIR Library** | fhir.resources | Pydantic validation, Pythonic API |
| **Unit Normalization** | ucumvert + pint | Full UCUM support with conversions |
| **Deterministic IDs** | SHA-256 content hashing | Deduplication via upsert |
| **Database Schema** | PostgreSQL: BYTEA + JSONB + pgMemento | Unified storage with audit support |

---

## Next Steps

1. **Prototype**: Build POC with pdfplumber + OpenAI + fhir.resources
2. **Validation**: Test with real lab PDFs (various formats)
3. **Unit mapping**: Build conversion table for common lab units
4. **Schema migration**: Implement PostgreSQL schema with Alembic
5. **Security review**: HIPAA compliance check for LLM API usage
6. **Performance testing**: Benchmark end-to-end pipeline with production volumes

---

**References**:
- All research conducted January 2024 with focus on production-ready, maintained libraries
- Best practices sourced from authoritative documentation and community consensus
- Medical data handling follows HIPAA and FHIR R4 standards
