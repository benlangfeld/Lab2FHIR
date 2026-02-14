# Data Model Specification: Lab PDF to FHIR Converter

**Feature**: Lab PDF to FHIR Converter  
**Tech Stack**: Python 3.11+, PostgreSQL, SQLAlchemy, Pydantic  
**Date**: 2024-02-14

---

## 1. Overview

This document defines the data model for the Lab PDF to FHIR Converter system. The model supports the complete lifecycle of lab report processing: patient management, PDF upload, text extraction, LLM parsing with intermediate representation, manual editing, FHIR bundle generation, and comprehensive audit logging.

### Design Principles

1. **Clear State Transitions**: Processing workflow progresses through well-defined states with audit logging
2. **Intermediate Contract**: Validated JSON schema serves as the contract between parsing and FHIR generation
3. **Source Preservation**: Original PDFs and intermediate representations are immutable and preserved
4. **Edit Tracking**: Manual corrections are versioned and auditable
5. **Deterministic Identity**: Content-based hashing enables deduplication and upsert operations
6. **Type Safety**: Pydantic models ensure runtime validation and SQLAlchemy provides database constraints

---

## 2. Entity Definitions

### 2.1 Patient

Represents a household member (human or veterinary) who is the subject of lab reports.

#### Purpose
- Allows multi-patient household management
- Provides subject references for FHIR resources
- Enables data separation between household members

#### SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

class PatientType(enum.Enum):
    HUMAN = "human"
    VETERINARY = "veterinary"

class Patient(Base):
    __tablename__ = "patients"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core Attributes
    display_name = Column(String(255), nullable=False, index=True)
    patient_type = Column(Enum(PatientType), nullable=False, default=PatientType.HUMAN)
    
    # Optional External Identifier
    external_identifier = Column(String(255), nullable=True, unique=True, index=True)
    external_identifier_system = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    notes = Column(Text, nullable=True)
    
    # Relationships
    uploads = relationship("Upload", back_populates="patient", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        {"comment": "Patient/subject profiles for household members (human and veterinary)"},
    )
```

#### Pydantic Schema

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum
from uuid import UUID

class PatientTypeEnum(str, Enum):
    HUMAN = "human"
    VETERINARY = "veterinary"

class PatientCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)
    patient_type: PatientTypeEnum = PatientTypeEnum.HUMAN
    external_identifier: str | None = Field(None, max_length=255)
    external_identifier_system: str | None = Field(None, max_length=255)
    notes: str | None = None

class PatientResponse(PatientCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### Business Rules
- `display_name` is required and must be non-empty
- `patient_type` defaults to "human"
- `external_identifier` must be unique if provided
- `external_identifier_system` should be provided when external_identifier is set (e.g., "MRN", "SSN", "VetID")

---

### 2.2 Upload

Represents an uploaded PDF lab report with processing lifecycle tracking.

#### Purpose
- Stores PDF binary data and metadata
- Tracks processing state from upload to completion
- Enables duplicate detection via SHA-256 hash
- Links to patient/subject

#### SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, Integer, LargeBinary, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

class UploadStatus(enum.Enum):
    UPLOADED = "uploaded"
    EXTRACTING = "extracting"
    PARSING = "parsing"
    REVIEW_PENDING = "review_pending"
    EDITING = "editing"
    VALIDATING = "validating"
    GENERATING_FHIR = "generating_fhir"
    REGENERATING_FHIR = "regenerating_fhir"
    COMPLETED = "completed"
    FAILED = "failed"

class Upload(Base):
    __tablename__ = "uploads"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File Metadata
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False, default="application/pdf")
    sha256_hash = Column(String(64), nullable=False, unique=True, index=True)
    
    # Binary Data
    pdf_data = Column(LargeBinary, nullable=False)
    
    # Processing State
    status = Column(Enum(UploadStatus), nullable=False, default=UploadStatus.UPLOADED, index=True)
    error_message = Column(Text, nullable=True)
    
    # Foreign Keys
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="uploads")
    intermediate_representations = relationship("IntermediateRepresentation", back_populates="upload", cascade="all, delete-orphan")
    fhir_bundles = relationship("FHIRBundle", back_populates="upload", cascade="all, delete-orphan")
    processing_logs = relationship("ProcessingLog", back_populates="upload", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("file_size_bytes > 0", name="check_file_size_positive"),
        {"comment": "Uploaded PDF lab reports with processing lifecycle tracking"},
    )
```

#### Pydantic Schema

```python
class UploadStatusEnum(str, Enum):
    UPLOADED = "uploaded"
    EXTRACTING = "extracting"
    PARSING = "parsing"
    REVIEW_PENDING = "review_pending"
    EDITING = "editing"
    VALIDATING = "validating"
    GENERATING_FHIR = "generating_fhir"
    REGENERATING_FHIR = "regenerating_fhir"
    COMPLETED = "completed"
    FAILED = "failed"

class UploadCreate(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    file_size_bytes: int = Field(..., gt=0)
    mime_type: str = Field(default="application/pdf", max_length=100)
    sha256_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    pdf_data: bytes
    patient_id: UUID

class UploadResponse(BaseModel):
    id: UUID
    file_name: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    status: UploadStatusEnum
    error_message: str | None
    patient_id: UUID
    uploaded_at: datetime
    processing_started_at: datetime | None
    processing_completed_at: datetime | None
    
    class Config:
        from_attributes = True
```

#### State Transitions

```
uploaded 
  → extracting (text extraction from PDF)
  → parsing (LLM structured extraction)
  → review_pending (awaiting user review)
  → [editing (user making corrections)]
  → validating (schema validation)
  → generating_fhir (FHIR bundle creation)
  → completed
  
OR at any stage → failed (with error_message)

From completed:
  → regenerating_fhir (bundle regeneration without re-parsing)
  → completed
```

#### Business Rules
- `sha256_hash` must be exactly 64 hexadecimal characters
- `sha256_hash` uniqueness prevents duplicate uploads
- `status` transitions must follow defined flow
- `error_message` should be populated when status is "failed"
- `processing_started_at` set when leaving "uploaded" state
- `processing_completed_at` set when reaching "completed" or "failed"

---

### 2.3 IntermediateRepresentation

Represents the validated JSON structure extracted from the PDF by the LLM, serving as the contract between parsing and FHIR generation.

#### Purpose
- Decouples LLM parsing from FHIR generation
- Enables manual verification and editing
- Provides audit trail of original vs. corrected data
- Allows FHIR regeneration without re-parsing

#### SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class IntermediateRepresentation(Base):
    __tablename__ = "intermediate_representations"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Versioning
    version = Column(Integer, nullable=False, default=1)
    is_current = Column(Boolean, nullable=False, default=True, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("intermediate_representations.id", ondelete="SET NULL"), nullable=True)
    
    # Content
    data = Column(JSONB, nullable=False)
    schema_version = Column(String(50), nullable=False, default="1.0.0")
    
    # Validation
    is_validated = Column(Boolean, nullable=False, default=False)
    validation_errors = Column(JSONB, nullable=True)
    
    # Edit Tracking
    is_edited = Column(Boolean, nullable=False, default=False)
    edit_summary = Column(Text, nullable=True)
    edited_by = Column(String(255), nullable=True)
    
    # Extraction Metadata
    extraction_method = Column(String(100), nullable=False)  # e.g., "gpt-4o", "claude-4.5"
    confidence_score = Column(Integer, nullable=True)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    upload = relationship("Upload", back_populates="intermediate_representations")
    children = relationship("IntermediateRepresentation", backref="parent", remote_side=[id])
    fhir_bundles = relationship("FHIRBundle", back_populates="intermediate_representation")
    
    # Constraints
    __table_args__ = (
        {"comment": "Validated intermediate JSON representations of lab data"},
    )
```

#### Pydantic Schema - Intermediate Data Structure

```python
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Literal

class LabMetadata(BaseModel):
    """Laboratory facility information"""
    lab_name: str | None = None
    lab_address: str | None = None
    lab_phone: str | None = None
    clia_number: str | None = None  # Clinical Laboratory Improvement Amendments ID

class AnalyteResult(BaseModel):
    """Individual lab test result"""
    analyte_name: str = Field(..., description="Test name as stated in report")
    analyte_code: str | None = Field(None, description="LOINC or local code")
    value: str = Field(..., description="Result value (numeric or qualitative)")
    value_type: Literal["numeric", "qualitative", "operator"] = "numeric"
    operator: str | None = Field(None, pattern=r"^(<|>|<=|>=)$")
    unit: str | None = Field(None, description="Unit of measurement")
    reference_range: str | None = None
    flag: str | None = Field(None, description="H/L/A/C flags")
    notes: str | None = None

class IntermediateData(BaseModel):
    """Validated intermediate schema for lab reports"""
    
    # Lab Information
    lab_metadata: LabMetadata
    
    # Report Identification
    report_id: str | None = None
    accession_number: str | None = None
    
    # Dates (ISO 8601 format: YYYY-MM-DD)
    collection_date: date = Field(..., description="Specimen collection date")
    result_date: date | None = Field(None, description="Result/test date if different from collection")
    report_date: date | None = Field(None, description="Report issued date")
    
    # Results
    analytes: list[AnalyteResult] = Field(..., min_length=1)
    
    # Additional Context
    specimen_type: str | None = None
    specimen_id: str | None = None
    ordering_provider: str | None = None
    clinical_info: str | None = None
    
    @field_validator('collection_date')
    @classmethod
    def validate_collection_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Collection date cannot be in the future")
        return v
    
    @field_validator('result_date')
    @classmethod
    def validate_result_date(cls, v: date | None) -> date | None:
        if v and v > date.today():
            raise ValueError("Result date cannot be in the future")
        return v

class IntermediateRepresentationCreate(BaseModel):
    upload_id: UUID
    data: IntermediateData
    schema_version: str = "1.0.0"
    extraction_method: str
    confidence_score: int | None = Field(None, ge=0, le=100)

class IntermediateRepresentationEdit(BaseModel):
    data: IntermediateData
    edit_summary: str | None = None
    edited_by: str | None = None

class IntermediateRepresentationResponse(BaseModel):
    id: UUID
    upload_id: UUID
    version: int
    is_current: bool
    parent_id: UUID | None
    data: IntermediateData
    schema_version: str
    is_validated: bool
    validation_errors: dict | None
    is_edited: bool
    edit_summary: str | None
    edited_by: str | None
    extraction_method: str
    confidence_score: int | None
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### Business Rules
- One upload can have multiple versions (original + edits)
- Only one version is marked `is_current = True` at a time
- `parent_id` links edited versions to their predecessor
- `version` increments with each edit
- `data` must validate against `IntermediateData` schema
- `is_validated = True` only after passing schema validation
- `validation_errors` stored as JSONB for detailed error reporting
- Original version always preserved (audit requirement)

---

### 2.4 FHIRBundle

Represents a generated FHIR R4 Bundle containing DiagnosticReport, Observations, and DocumentReference.

#### Purpose
- Stores validated FHIR resources ready for submission
- Links to source intermediate representation
- Supports bundle regeneration
- Tracks validation status

#### SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class FHIRBundle(Base):
    __tablename__ = "fhir_bundles"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    intermediate_representation_id = Column(UUID(as_uuid=True), ForeignKey("intermediate_representations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Bundle Content
    bundle_data = Column(JSONB, nullable=False)
    bundle_type = Column(String(50), nullable=False, default="transaction")
    
    # Resource Tracking
    resource_ids = Column(ARRAY(String), nullable=False)  # Array of FHIR resource IDs
    resource_types = Column(ARRAY(String), nullable=False)  # Corresponding resource types
    
    # Validation
    is_valid = Column(Boolean, nullable=False, default=False)
    validation_errors = Column(JSONB, nullable=True)
    validator_version = Column(String(50), nullable=True)  # fhir.resources version
    
    # Generation Metadata
    generation_method = Column(String(100), nullable=False, default="automated")
    is_regenerated = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    upload = relationship("Upload", back_populates="fhir_bundles")
    intermediate_representation = relationship("IntermediateRepresentation", back_populates="fhir_bundles")
    
    # Constraints
    __table_args__ = (
        {"comment": "Generated FHIR R4 Bundles ready for submission"},
    )
```

#### Pydantic Schema

```python
class FHIRBundleResponse(BaseModel):
    id: UUID
    upload_id: UUID
    intermediate_representation_id: UUID
    bundle_data: dict  # Full FHIR Bundle JSON
    bundle_type: str
    resource_ids: list[str]
    resource_types: list[str]
    is_valid: bool
    validation_errors: dict | None
    validator_version: str | None
    generation_method: str
    is_regenerated: bool
    generated_at: datetime
    
    class Config:
        from_attributes = True

class FHIRBundleCreate(BaseModel):
    upload_id: UUID
    intermediate_representation_id: UUID
    bundle_data: dict
    resource_ids: list[str]
    resource_types: list[str]
    validator_version: str
```

#### FHIR Bundle Structure

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "DocumentReference",
        "id": "doc-{deterministic_hash}",
        "status": "current",
        "content": [{
          "attachment": {
            "contentType": "application/pdf",
            "data": "{base64_encoded_pdf}"
          }
        }]
      },
      "request": {
        "method": "PUT",
        "url": "DocumentReference/doc-{deterministic_hash}"
      }
    },
    {
      "resource": {
        "resourceType": "DiagnosticReport",
        "id": "dr-{deterministic_hash}",
        "status": "final",
        "subject": {"reference": "Patient/{patient_id}"},
        "result": [
          {"reference": "Observation/obs-{deterministic_hash}"}
        ]
      },
      "request": {
        "method": "PUT",
        "url": "DiagnosticReport/dr-{deterministic_hash}"
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-{deterministic_hash}",
        "status": "final",
        "code": {"coding": [{"code": "LOINC_CODE"}]},
        "subject": {"reference": "Patient/{patient_id}"},
        "valueQuantity": {"value": 5.2, "unit": "mg/dL"}
      },
      "request": {
        "method": "PUT",
        "url": "Observation/obs-{deterministic_hash}"
      }
    }
  ]
}
```

#### Deterministic ID Generation

```python
import hashlib
import json

def generate_deterministic_id(resource_type: str, key_fields: dict[str, Any]) -> str:
    """
    Generate deterministic FHIR resource ID.
    
    Args:
        resource_type: FHIR resource type (e.g., "Observation")
        key_fields: Stable identifying fields (patient_id, collection_date, analyte, value, unit)
    
    Returns:
        Deterministic ID in format: {prefix}-{hash_16_chars}
    """
    canonical = {
        "resourceType": resource_type,
        "scope": "lab2fhir",
        **{k: key_fields[k] for k in sorted(key_fields.keys())}
    }
    canonical_json = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
    hash_digest = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    prefix = resource_type[:3].lower()
    return f"{prefix}-{hash_digest[:16]}"

# Example usage for Observation
obs_id = generate_deterministic_id(
    "Observation",
    {
        "patient_id": "550e8400-e29b-41d4-a716-446655440000",
        "collection_date": "2024-01-15",
        "analyte_name": "Glucose",
        "value": "95",
        "unit": "mg/dL"
    }
)
# Result: "obs-a3f5b1c2d4e6f7a8"
```

#### Business Rules
- One bundle per intermediate representation (can regenerate to create new bundle)
- `bundle_type` is always "transaction" for atomic submission
- `resource_ids` and `resource_types` arrays have same length and corresponding order
- `is_valid = True` only after FHIR R4 validation passes
- `is_regenerated = True` when bundle created from existing intermediate representation
- All resource IDs in bundle must be deterministic and reproducible

---

### 2.5 ProcessingLog

Comprehensive audit trail of all processing events and state transitions.

#### Purpose
- Provides complete audit trail for compliance
- Tracks state transitions and processing steps
- Captures errors and warnings
- Enables debugging and monitoring

#### SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class LogLevel(enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ProcessingLog(Base):
    __tablename__ = "processing_logs"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Log Entry
    log_level = Column(Enum(LogLevel), nullable=False, default=LogLevel.INFO, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # "state_transition", "validation", "error", etc.
    message = Column(Text, nullable=False)
    
    # Context Data
    context = Column(JSONB, nullable=True)  # Additional structured data
    
    # Processing Stage
    stage = Column(String(100), nullable=True)  # "extraction", "parsing", "fhir_generation", etc.
    duration_ms = Column(Integer, nullable=True)  # Duration in milliseconds
    
    # Source
    component = Column(String(100), nullable=True)  # "pdf_extractor", "llm_parser", "fhir_generator", etc.
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Relationships
    upload = relationship("Upload", back_populates="processing_logs")
    
    # Constraints
    __table_args__ = (
        {"comment": "Audit log of all processing events and state transitions"},
    )
```

#### Pydantic Schema

```python
class LogLevelEnum(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ProcessingLogCreate(BaseModel):
    upload_id: UUID
    log_level: LogLevelEnum
    event_type: str = Field(..., max_length=100)
    message: str
    context: dict | None = None
    stage: str | None = Field(None, max_length=100)
    duration_ms: int | None = Field(None, ge=0)
    component: str | None = Field(None, max_length=100)

class ProcessingLogResponse(BaseModel):
    id: UUID
    upload_id: UUID
    log_level: LogLevelEnum
    event_type: str
    message: str
    context: dict | None
    stage: str | None
    duration_ms: int | None
    component: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### Common Event Types

```python
# State Transitions
EVENT_UPLOAD_CREATED = "upload_created"
EVENT_STATE_TRANSITION = "state_transition"

# PDF Processing
EVENT_EXTRACTION_STARTED = "extraction_started"
EVENT_EXTRACTION_COMPLETED = "extraction_completed"
EVENT_EXTRACTION_FAILED = "extraction_failed"

# LLM Parsing
EVENT_PARSING_STARTED = "parsing_started"
EVENT_PARSING_COMPLETED = "parsing_completed"
EVENT_PARSING_FAILED = "parsing_failed"

# Validation
EVENT_VALIDATION_STARTED = "validation_started"
EVENT_VALIDATION_PASSED = "validation_passed"
EVENT_VALIDATION_FAILED = "validation_failed"

# Editing
EVENT_EDIT_STARTED = "edit_started"
EVENT_EDIT_SAVED = "edit_saved"
EVENT_EDIT_CANCELLED = "edit_cancelled"

# FHIR Generation
EVENT_FHIR_GENERATION_STARTED = "fhir_generation_started"
EVENT_FHIR_GENERATION_COMPLETED = "fhir_generation_completed"
EVENT_FHIR_GENERATION_FAILED = "fhir_generation_failed"
EVENT_FHIR_REGENERATION_STARTED = "fhir_regeneration_started"

# Errors
EVENT_ERROR = "error"
EVENT_WARNING = "warning"

# Duplicates
EVENT_DUPLICATE_DETECTED = "duplicate_detected"
```

#### Business Rules
- All state transitions must be logged
- Errors must include `context` with stack traces or relevant data
- `duration_ms` should be captured for performance-critical operations
- `component` identifies which system component generated the log

---

## 3. Relationships Summary

```
Patient (1) ──────< (Many) Upload
                            │
                            ├──< (Many) IntermediateRepresentation
                            │             │
                            │             └──< (Many) FHIRBundle
                            │
                            └──< (Many) ProcessingLog

IntermediateRepresentation (Self-referencing for edit versioning)
  └── parent_id ──> IntermediateRepresentation.id
```

---

## 4. Database Schema (PostgreSQL DDL)

```sql
-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- ENUMS
-- ========================================

CREATE TYPE patient_type AS ENUM ('human', 'veterinary');
CREATE TYPE upload_status AS ENUM (
    'uploaded', 'extracting', 'parsing', 'review_pending', 'editing',
    'validating', 'generating_fhir', 'regenerating_fhir', 'completed', 'failed'
);
CREATE TYPE log_level AS ENUM ('debug', 'info', 'warning', 'error', 'critical');

-- ========================================
-- PATIENTS TABLE
-- ========================================

CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    display_name VARCHAR(255) NOT NULL,
    patient_type patient_type NOT NULL DEFAULT 'human',
    external_identifier VARCHAR(255) UNIQUE,
    external_identifier_system VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT
);

CREATE INDEX idx_patients_display_name ON patients(display_name);
CREATE INDEX idx_patients_external_identifier ON patients(external_identifier) WHERE external_identifier IS NOT NULL;

COMMENT ON TABLE patients IS 'Patient/subject profiles for household members (human and veterinary)';

-- ========================================
-- UPLOADS TABLE
-- ========================================

CREATE TABLE uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes INTEGER NOT NULL CHECK (file_size_bytes > 0),
    mime_type VARCHAR(100) NOT NULL DEFAULT 'application/pdf',
    sha256_hash CHAR(64) NOT NULL UNIQUE,
    pdf_data BYTEA NOT NULL,
    status upload_status NOT NULL DEFAULT 'uploaded',
    error_message TEXT,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    CONSTRAINT check_hash_format CHECK (sha256_hash ~ '^[a-f0-9]{64}$')
);

CREATE INDEX idx_uploads_sha256_hash ON uploads(sha256_hash);
CREATE INDEX idx_uploads_status ON uploads(status);
CREATE INDEX idx_uploads_patient_id ON uploads(patient_id);
CREATE INDEX idx_uploads_uploaded_at ON uploads(uploaded_at);

COMMENT ON TABLE uploads IS 'Uploaded PDF lab reports with processing lifecycle tracking';

-- ========================================
-- INTERMEDIATE REPRESENTATIONS TABLE
-- ========================================

CREATE TABLE intermediate_representations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    upload_id UUID NOT NULL REFERENCES uploads(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    parent_id UUID REFERENCES intermediate_representations(id) ON DELETE SET NULL,
    data JSONB NOT NULL,
    schema_version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    is_validated BOOLEAN NOT NULL DEFAULT FALSE,
    validation_errors JSONB,
    is_edited BOOLEAN NOT NULL DEFAULT FALSE,
    edit_summary TEXT,
    edited_by VARCHAR(255),
    extraction_method VARCHAR(100) NOT NULL,
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_intermediate_representations_upload_id ON intermediate_representations(upload_id);
CREATE INDEX idx_intermediate_representations_is_current ON intermediate_representations(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_intermediate_representations_data ON intermediate_representations USING GIN(data);

COMMENT ON TABLE intermediate_representations IS 'Validated intermediate JSON representations of lab data';

-- ========================================
-- FHIR BUNDLES TABLE
-- ========================================

CREATE TABLE fhir_bundles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    upload_id UUID NOT NULL REFERENCES uploads(id) ON DELETE CASCADE,
    intermediate_representation_id UUID NOT NULL REFERENCES intermediate_representations(id) ON DELETE CASCADE,
    bundle_data JSONB NOT NULL,
    bundle_type VARCHAR(50) NOT NULL DEFAULT 'transaction',
    resource_ids TEXT[] NOT NULL,
    resource_types TEXT[] NOT NULL,
    is_valid BOOLEAN NOT NULL DEFAULT FALSE,
    validation_errors JSONB,
    validator_version VARCHAR(50),
    generation_method VARCHAR(100) NOT NULL DEFAULT 'automated',
    is_regenerated BOOLEAN NOT NULL DEFAULT FALSE,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fhir_bundles_upload_id ON fhir_bundles(upload_id);
CREATE INDEX idx_fhir_bundles_intermediate_representation_id ON fhir_bundles(intermediate_representation_id);
CREATE INDEX idx_fhir_bundles_bundle_data ON fhir_bundles USING GIN(bundle_data);
CREATE INDEX idx_fhir_bundles_resource_ids ON fhir_bundles USING GIN(resource_ids);

COMMENT ON TABLE fhir_bundles IS 'Generated FHIR R4 Bundles ready for submission';

-- ========================================
-- PROCESSING LOGS TABLE
-- ========================================

CREATE TABLE processing_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    upload_id UUID NOT NULL REFERENCES uploads(id) ON DELETE CASCADE,
    log_level log_level NOT NULL DEFAULT 'info',
    event_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    context JSONB,
    stage VARCHAR(100),
    duration_ms INTEGER CHECK (duration_ms >= 0),
    component VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_processing_logs_upload_id ON processing_logs(upload_id);
CREATE INDEX idx_processing_logs_log_level ON processing_logs(log_level);
CREATE INDEX idx_processing_logs_event_type ON processing_logs(event_type);
CREATE INDEX idx_processing_logs_created_at ON processing_logs(created_at);
CREATE INDEX idx_processing_logs_context ON processing_logs USING GIN(context);

COMMENT ON TABLE processing_logs IS 'Audit log of all processing events and state transitions';

-- ========================================
-- FUNCTIONS AND TRIGGERS
-- ========================================

-- Auto-update updated_at timestamp for patients
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## 5. Validation Rules

### 5.1 Upload Validation

```python
def validate_upload(upload: UploadCreate) -> None:
    """Validate upload before database insertion."""
    
    # File size limits (e.g., 50 MB max)
    if upload.file_size_bytes > 50 * 1024 * 1024:
        raise ValueError("File size exceeds 50 MB limit")
    
    # MIME type validation
    if upload.mime_type != "application/pdf":
        raise ValueError("Only PDF files are supported")
    
    # SHA-256 hash format
    if not re.match(r'^[a-f0-9]{64}$', upload.sha256_hash):
        raise ValueError("Invalid SHA-256 hash format")
    
    # PDF data validation
    if len(upload.pdf_data) != upload.file_size_bytes:
        raise ValueError("File size mismatch with binary data length")
```

### 5.2 Duplicate Detection

```python
import hashlib

def calculate_file_hash(file_data: bytes) -> str:
    """Calculate SHA-256 hash of file content."""
    return hashlib.sha256(file_data).hexdigest()

def check_duplicate(session, sha256_hash: str) -> Upload | None:
    """Check if upload already exists."""
    return session.query(Upload).filter_by(sha256_hash=sha256_hash).first()
```

### 5.3 Intermediate Schema Validation

```python
from pydantic import ValidationError

def validate_intermediate_data(data: dict) -> tuple[bool, list[str]]:
    """
    Validate intermediate representation against schema.
    
    Returns:
        (is_valid, error_messages)
    """
    try:
        IntermediateData.model_validate(data)
        return (True, [])
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        return (False, errors)
```

### 5.4 State Transition Validation

```python
# Valid state transitions
STATE_TRANSITIONS = {
    UploadStatus.UPLOADED: [UploadStatus.EXTRACTING, UploadStatus.FAILED],
    UploadStatus.EXTRACTING: [UploadStatus.PARSING, UploadStatus.FAILED],
    UploadStatus.PARSING: [UploadStatus.REVIEW_PENDING, UploadStatus.FAILED],
    UploadStatus.REVIEW_PENDING: [UploadStatus.EDITING, UploadStatus.VALIDATING, UploadStatus.FAILED],
    UploadStatus.EDITING: [UploadStatus.VALIDATING, UploadStatus.REVIEW_PENDING, UploadStatus.FAILED],
    UploadStatus.VALIDATING: [UploadStatus.GENERATING_FHIR, UploadStatus.FAILED],
    UploadStatus.GENERATING_FHIR: [UploadStatus.COMPLETED, UploadStatus.FAILED],
    UploadStatus.COMPLETED: [UploadStatus.REGENERATING_FHIR],
    UploadStatus.REGENERATING_FHIR: [UploadStatus.COMPLETED, UploadStatus.FAILED],
    UploadStatus.FAILED: [],  # Terminal state
}

def validate_state_transition(current: UploadStatus, next_state: UploadStatus) -> bool:
    """Validate if state transition is allowed."""
    return next_state in STATE_TRANSITIONS.get(current, [])
```

---

## 6. Migration Strategy (Alembic)

```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create enums
    patient_type_enum = postgresql.ENUM('human', 'veterinary', name='patient_type')
    patient_type_enum.create(op.get_bind())
    
    upload_status_enum = postgresql.ENUM(
        'uploaded', 'extracting', 'parsing', 'review_pending', 'editing',
        'validating', 'generating_fhir', 'regenerating_fhir', 'completed', 'failed',
        name='upload_status'
    )
    upload_status_enum.create(op.get_bind())
    
    log_level_enum = postgresql.ENUM('debug', 'info', 'warning', 'error', 'critical', name='log_level')
    log_level_enum.create(op.get_bind())
    
    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('patient_type', patient_type_enum, nullable=False, server_default='human'),
        sa.Column('external_identifier', sa.String(255), unique=True),
        sa.Column('external_identifier_system', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('notes', sa.Text)
    )
    
    # Continue with other tables...

def downgrade():
    op.drop_table('processing_logs')
    op.drop_table('fhir_bundles')
    op.drop_table('intermediate_representations')
    op.drop_table('uploads')
    op.drop_table('patients')
    
    # Drop enums
    sa.Enum(name='log_level').drop(op.get_bind())
    sa.Enum(name='upload_status').drop(op.get_bind())
    sa.Enum(name='patient_type').drop(op.get_bind())
```

---

## 7. Indexes and Performance Optimization

### 7.1 Recommended Indexes

```sql
-- Already covered in schema, but key indexes:

-- Lookups by hash for duplicate detection
CREATE INDEX idx_uploads_sha256_hash ON uploads(sha256_hash);

-- Processing status queries
CREATE INDEX idx_uploads_status ON uploads(status);

-- Current version lookups
CREATE INDEX idx_intermediate_representations_is_current 
    ON intermediate_representations(is_current) WHERE is_current = TRUE;

-- JSON queries
CREATE INDEX idx_intermediate_representations_data 
    ON intermediate_representations USING GIN(data);

-- Log filtering
CREATE INDEX idx_processing_logs_event_type ON processing_logs(event_type);
CREATE INDEX idx_processing_logs_created_at ON processing_logs(created_at);
```

### 7.2 Query Optimization Examples

```python
# Efficient duplicate check
def find_duplicate(session, sha256_hash: str) -> Upload | None:
    return session.query(Upload).filter_by(sha256_hash=sha256_hash).first()

# Get current intermediate representation
def get_current_intermediate(session, upload_id: UUID) -> IntermediateRepresentation | None:
    return (
        session.query(IntermediateRepresentation)
        .filter_by(upload_id=upload_id, is_current=True)
        .first()
    )

# Get processing history with logs
def get_upload_with_logs(session, upload_id: UUID):
    upload = session.query(Upload).filter_by(id=upload_id).first()
    logs = (
        session.query(ProcessingLog)
        .filter_by(upload_id=upload_id)
        .order_by(ProcessingLog.created_at)
        .all()
    )
    return upload, logs
```

---

## 8. Data Retention and Cleanup

### 8.1 Retention Policies

```python
# Example retention policy: Archive completed uploads after 1 year
from datetime import datetime, timedelta

def archive_old_uploads(session, days_threshold: int = 365):
    """Archive uploads older than threshold."""
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    
    old_uploads = (
        session.query(Upload)
        .filter(
            Upload.status == UploadStatus.COMPLETED,
            Upload.processing_completed_at < cutoff_date
        )
        .all()
    )
    
    # Archive logic (e.g., move to cold storage, export to S3)
    return len(old_uploads)
```

### 8.2 Cascading Deletes

All relationships use `ON DELETE CASCADE` to ensure referential integrity:
- Deleting a Patient cascades to all related Uploads
- Deleting an Upload cascades to IntermediateRepresentations, FHIRBundles, and ProcessingLogs
- Deleting an IntermediateRepresentation cascades to FHIRBundles

---

## 9. Security Considerations

### 9.1 PHI Handling

```python
# Never log PHI in plaintext
def log_processing_event(session, upload_id: UUID, message: str, context: dict):
    # Sanitize context to remove PHI
    safe_context = {
        k: v for k, v in context.items() 
        if k not in ['patient_name', 'ssn', 'address', 'phone']
    }
    
    log = ProcessingLog(
        upload_id=upload_id,
        message=message,
        context=safe_context
    )
    session.add(log)
```

### 9.2 Access Control

```python
# Row-level security example (PostgreSQL RLS)
# Enable RLS on patients table
"""
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;

CREATE POLICY patient_isolation ON patients
    USING (user_id = current_setting('app.current_user_id')::uuid);
"""
```

---

## 10. Testing Strategies

### 10.1 Unit Tests

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine("postgresql://test:test@localhost/test_lab2fhir")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

def test_duplicate_detection(db_session):
    # Create first upload
    upload1 = Upload(
        file_name="test.pdf",
        file_size_bytes=1024,
        sha256_hash="a" * 64,
        pdf_data=b"test",
        patient_id=uuid.uuid4()
    )
    db_session.add(upload1)
    db_session.commit()
    
    # Try to create duplicate
    upload2 = Upload(
        file_name="test2.pdf",
        file_size_bytes=1024,
        sha256_hash="a" * 64,  # Same hash
        pdf_data=b"test",
        patient_id=uuid.uuid4()
    )
    
    with pytest.raises(IntegrityError):
        db_session.add(upload2)
        db_session.commit()

def test_state_transition_validation(db_session):
    upload = Upload(
        file_name="test.pdf",
        file_size_bytes=1024,
        sha256_hash="b" * 64,
        pdf_data=b"test",
        patient_id=uuid.uuid4(),
        status=UploadStatus.UPLOADED
    )
    db_session.add(upload)
    db_session.commit()
    
    # Valid transition
    assert validate_state_transition(upload.status, UploadStatus.EXTRACTING)
    
    # Invalid transition
    assert not validate_state_transition(upload.status, UploadStatus.COMPLETED)
```

### 10.2 Integration Tests

```python
def test_full_processing_workflow(db_session):
    # Create patient
    patient = Patient(display_name="John Doe")
    db_session.add(patient)
    db_session.commit()
    
    # Upload PDF
    upload = Upload(
        file_name="lab_report.pdf",
        file_size_bytes=5000,
        sha256_hash="c" * 64,
        pdf_data=b"fake_pdf_data",
        patient_id=patient.id
    )
    db_session.add(upload)
    db_session.commit()
    
    # Create intermediate representation
    intermediate_data = {
        "lab_metadata": {"lab_name": "Test Lab"},
        "collection_date": "2024-01-15",
        "analytes": [
            {
                "analyte_name": "Glucose",
                "value": "95",
                "value_type": "numeric",
                "unit": "mg/dL",
                "reference_range": "70-100"
            }
        ]
    }
    
    intermediate = IntermediateRepresentation(
        upload_id=upload.id,
        data=intermediate_data,
        extraction_method="gpt-4o",
        is_validated=True
    )
    db_session.add(intermediate)
    db_session.commit()
    
    # Generate FHIR bundle
    bundle = FHIRBundle(
        upload_id=upload.id,
        intermediate_representation_id=intermediate.id,
        bundle_data={"resourceType": "Bundle", "type": "transaction"},
        resource_ids=["obs-123", "dr-456"],
        resource_types=["Observation", "DiagnosticReport"],
        is_valid=True
    )
    db_session.add(bundle)
    db_session.commit()
    
    # Verify complete chain
    assert upload.intermediate_representations[0] == intermediate
    assert upload.fhir_bundles[0] == bundle
    assert bundle.intermediate_representation == intermediate
```

---

## 11. Summary

This data model provides:

1. **Complete Processing Lifecycle**: From PDF upload through intermediate representation to FHIR bundle generation
2. **Audit Trail**: Comprehensive logging of all processing events and state transitions
3. **Edit Versioning**: Full history of manual corrections with original data preservation
4. **Duplicate Prevention**: SHA-256 hash-based deduplication at upload level
5. **Type Safety**: Pydantic schemas ensure runtime validation; SQLAlchemy provides database constraints
6. **FHIR Compliance**: Structured to support FHIR R4 resource generation with deterministic IDs
7. **Multi-Patient Support**: Household-scale health record management
8. **Regeneration Capability**: FHIR bundles can be regenerated from stored intermediate representations

### Key Design Decisions

- **PostgreSQL with JSONB**: Combines relational integrity with flexible JSON storage for intermediate data and FHIR bundles
- **Intermediate Schema Contract**: Validated JSON structure decouples LLM parsing from FHIR generation
- **Deterministic IDs**: Content-based hashing enables idempotent operations and deduplication
- **Cascading Relationships**: Simplifies cleanup while maintaining referential integrity
- **State Machine**: Explicit state transitions with validation ensure processing integrity

---

## 12. Next Steps

1. **Implement Alembic migrations** for schema versioning
2. **Create SQLAlchemy models** matching this specification
3. **Define Pydantic schemas** for API request/response validation
4. **Implement state transition logic** with validation
5. **Build deterministic ID generation** utility functions
6. **Create database indexes** for query optimization
7. **Set up unit tests** for models and validation logic
8. **Document API endpoints** that interact with these entities
