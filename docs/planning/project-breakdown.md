# Lab2FHIR - Project Breakdown

**Methodology**: Kanban (continuous flow, no sprints or milestones)  
**Approach**: MVP-first with iterative polish  
**Tech Stack**: Python, OpenAI API, FHIR R4, Heroku, PostgreSQL  
**Development Environment**: GitHub Codespaces, Actions, Copilot

---

## Epic Structure

This project is organized into 6 epics that follow the data flow:

1. **Project Infrastructure & Development Environment** - Foundation
2. **PDF Ingestion Layer** - Accept and store PDFs
3. **LLM Parsing Layer** - Extract structured data from PDFs
4. **Normalization & Validation Layer** - Clean and validate data
5. **FHIR Generation Layer** - Convert to FHIR resources
6. **FHIR Store Integration** - Push to FHIR server

---

## Epic 1: Project Infrastructure & Development Environment

**Goal**: Set up a production-ready Python development environment with CI/CD

### Features

#### F1.1: Python Project Structure
- **Task 1.1.1**: Initialize Python project with pyproject.toml
- **Task 1.1.2**: Set up package structure (src/lab2fhir/)
- **Task 1.1.3**: Configure Poetry for dependency management
- **Task 1.1.4**: Add .gitignore for Python projects

#### F1.2: Development Environment
- **Task 1.2.1**: Create devcontainer.json for GitHub Codespaces
- **Task 1.2.2**: Configure VS Code settings and extensions
- **Task 1.2.3**: Add development dependencies (pytest, black, ruff, mypy)
- **Task 1.2.4**: Create Makefile with common commands

#### F1.3: Code Quality & Linting
- **Task 1.3.1**: Configure Ruff for linting and formatting
- **Task 1.3.2**: Configure mypy for type checking
- **Task 1.3.3**: Set up pre-commit hooks
- **Task 1.3.4**: Add code quality checks to CI

#### F1.4: Testing Infrastructure
- **Task 1.4.1**: Set up pytest with coverage reporting
- **Task 1.4.2**: Create test fixtures for sample PDFs
- **Task 1.4.3**: Add test utilities and helpers
- **Task 1.4.4**: Configure coverage thresholds

#### F1.5: CI/CD Pipeline
- **Task 1.5.1**: Create GitHub Actions workflow for tests
- **Task 1.5.2**: Create GitHub Actions workflow for linting
- **Task 1.5.3**: Add security scanning (Dependabot, CodeQL)
- **Task 1.5.4**: Set up automated dependency updates

#### F1.6: Documentation
- **Task 1.6.1**: Create CONTRIBUTING.md
- **Task 1.6.2**: Create architecture documentation
- **Task 1.6.3**: Set up API documentation with Sphinx
- **Task 1.6.4**: Add inline code documentation standards

---

## Epic 2: PDF Ingestion Layer

**Goal**: Accept PDF uploads, deduplicate, and prepare for processing

### Features

#### F2.1: Storage Backend
- **Task 2.1.1**: Set up PostgreSQL database schema
- **Task 2.1.2**: Create SQLAlchemy models for documents
- **Task 2.1.3**: Implement database migrations with Alembic
- **Task 2.1.4**: Add database connection pooling

#### F2.2: PDF Upload Handler
- **Task 2.2.1**: Create Flask/FastAPI web application skeleton
- **Task 2.2.2**: Implement PDF upload endpoint
- **Task 2.2.3**: Add file validation (size, type, format)
- **Task 2.2.4**: Store uploaded PDFs (filesystem or blob storage)

#### F2.3: Document Management
- **Task 2.3.1**: Implement file hash calculation for deduplication
- **Task 2.3.2**: Create document metadata storage
- **Task 2.3.3**: Add patient/subject association logic
- **Task 2.3.4**: Implement document status tracking

#### F2.4: Multi-Patient Support
- **Task 2.4.1**: Create patient/subject data model
- **Task 2.4.2**: Add patient selection UI/API
- **Task 2.4.3**: Implement patient-level access control
- **Task 2.4.4**: Add household/family grouping support

---

## Epic 3: LLM Parsing Layer

**Goal**: Extract structured lab data from PDF text using LLM with strict schema

### Features

#### F3.1: PDF Text Extraction
- **Task 3.1.1**: Evaluate and select PDF parsing library (PyPDF2, pdfplumber, etc.)
- **Task 3.1.2**: Implement text extraction pipeline
- **Task 3.1.3**: Handle multi-page PDFs
- **Task 3.1.4**: Add text quality validation

#### F3.2: LLM Schema Design
- **Task 3.2.1**: Define intermediate JSON schema for lab results
- **Task 3.2.2**: Create Pydantic models for validation
- **Task 3.2.3**: Document schema with examples
- **Task 3.2.4**: Version schema for future changes

#### F3.3: OpenAI Integration
- **Task 3.3.1**: Set up OpenAI API client
- **Task 3.3.2**: Implement structured output with function calling
- **Task 3.3.3**: Create prompt templates for lab parsing
- **Task 3.3.4**: Add retry logic and error handling

#### F3.4: Parse Result Storage
- **Task 3.4.1**: Store intermediate JSON results in database
- **Task 3.4.2**: Link parsed results to source PDFs
- **Task 3.4.3**: Add parsing status and error tracking
- **Task 3.4.4**: Implement parse result versioning

#### F3.5: Quality Assurance
- **Task 3.5.1**: Add confidence scoring for extracted values
- **Task 3.5.2**: Flag ambiguous or low-confidence results
- **Task 3.5.3**: Create human review queue for flagged items
- **Task 3.5.4**: Add parsing metrics and monitoring

---

## Epic 4: Normalization & Validation Layer

**Goal**: Clean, validate, and normalize extracted lab data

### Features

#### F4.1: Unit Normalization
- **Task 4.1.1**: Create unit conversion library
- **Task 4.1.2**: Implement common lab unit standardization
- **Task 4.1.3**: Handle unit ambiguity and variants
- **Task 4.1.4**: Add unit validation rules

#### F4.2: Date Normalization
- **Task 4.2.1**: Parse various date formats
- **Task 4.2.2**: Handle timezone considerations
- **Task 4.2.3**: Validate date ranges and logical constraints
- **Task 4.2.4**: Store original and normalized dates

#### F4.3: Value Validation
- **Task 4.3.1**: Validate numeric vs qualitative values
- **Task 4.3.2**: Check values against reference ranges
- **Task 4.3.3**: Detect and flag outliers
- **Task 4.3.4**: Validate data type consistency

#### F4.4: Analyte Name Canonicalization
- **Task 4.4.1**: Create analyte name mapping database
- **Task 4.4.2**: Implement fuzzy matching for variants
- **Task 4.4.3**: Handle common abbreviations
- **Task 4.4.4**: Support custom analyte definitions

#### F4.5: Data Quality Checks
- **Task 4.5.1**: Implement cross-field validation
- **Task 4.5.2**: Check for missing required fields
- **Task 4.5.3**: Validate reference range formats
- **Task 4.5.4**: Generate data quality reports

---

## Epic 5: FHIR Generation Layer

**Goal**: Convert normalized data into valid FHIR R4 resources

### Features

#### F5.1: FHIR Library Integration
- **Task 5.1.1**: Select and integrate FHIR library (fhir.resources)
- **Task 5.1.2**: Set up FHIR resource builders
- **Task 5.1.3**: Add FHIR validation
- **Task 5.1.4**: Configure FHIR resource profiles

#### F5.2: Observation Generation
- **Task 5.2.1**: Create Observation resources from analytes
- **Task 5.2.2**: Map values and units to FHIR structure
- **Task 5.2.3**: Add reference ranges to Observations
- **Task 5.2.4**: Implement observation identifiers for deduplication

#### F5.3: DiagnosticReport Generation
- **Task 5.3.1**: Create DiagnosticReport for lab panels
- **Task 5.3.2**: Link Observations to DiagnosticReport
- **Task 5.3.3**: Add metadata (lab, performer, dates)
- **Task 5.3.4**: Generate deterministic DiagnosticReport IDs

#### F5.4: DocumentReference Generation
- **Task 5.4.1**: Create DocumentReference for original PDF
- **Task 5.4.2**: Link PDF content (base64 or URL)
- **Task 5.4.3**: Add document metadata
- **Task 5.4.4**: Set document relationships

#### F5.5: Bundle Creation
- **Task 5.5.1**: Create transaction Bundle
- **Task 5.5.2**: Include all resources in Bundle
- **Task 5.5.3**: Set Bundle identifiers
- **Task 5.5.4**: Validate complete Bundle

#### F5.6: Patient Resource Handling
- **Task 5.6.1**: Create or reference Patient resources
- **Task 5.6.2**: Handle patient identifiers
- **Task 5.6.3**: Support both human and veterinary patients
- **Task 5.6.4**: Implement patient matching logic

---

## Epic 6: FHIR Store Integration

**Goal**: Push FHIR bundles to FHIR server with retry and status tracking

### Features

#### F6.1: FHIR Server Client
- **Task 6.1.1**: Implement generic FHIR HTTP client
- **Task 6.1.2**: Add authentication support (OAuth, API key)
- **Task 6.1.3**: Configure for Fasten and other servers
- **Task 6.1.4**: Add connection testing endpoint

#### F6.2: Bundle Submission
- **Task 6.2.1**: POST transaction bundles to FHIR server
- **Task 6.2.2**: Handle FHIR server responses
- **Task 6.2.3**: Parse and store operation outcomes
- **Task 6.2.4**: Update document status after submission

#### F6.3: Error Handling & Retry
- **Task 6.3.1**: Implement exponential backoff retry
- **Task 6.3.2**: Handle transient vs permanent failures
- **Task 6.3.3**: Store failed submissions for review
- **Task 6.3.4**: Add manual retry capability

#### F6.4: Status Tracking
- **Task 6.4.1**: Track submission lifecycle states
- **Task 6.4.2**: Create status dashboard/API
- **Task 6.4.3**: Add submission history logs
- **Task 6.4.4**: Implement submission metrics

#### F6.5: Deduplication Logic
- **Task 6.5.1**: Implement deterministic ID generation
- **Task 6.5.2**: Check for existing resources before submit
- **Task 6.5.3**: Handle reprocessing scenarios
- **Task 6.5.4**: Add forced resubmission flag

---

## MVP Definition (v0.1)

**Goal**: Demonstrate end-to-end PDF → FHIR flow with single patient

### Must-Have Features
- Basic Python project structure
- Simple PDF upload (no UI, API only)
- PDF text extraction
- OpenAI parsing with basic schema
- Basic FHIR Observation generation
- Manual FHIR bundle output (no server push yet)

### MVP Task Sequence
1. Initialize Python project (F1.1)
2. Set up development environment (F1.2, F1.3)
3. Create basic web API (F2.2, Tasks 1-2)
4. Implement PDF text extraction (F3.1)
5. Create basic LLM schema (F3.2, Tasks 1-2)
6. Integrate OpenAI API (F3.3, Tasks 1-3)
7. Build minimal FHIR generator (F5.1, F5.2)
8. Output FHIR bundle to file/stdout

---

## Post-MVP Iterations

### Iteration 1: Polish MVP
- Add comprehensive tests
- Improve error handling
- Add logging and monitoring
- Documentation

### Iteration 2: Database Persistence
- Add PostgreSQL support
- Store documents and results
- Implement status tracking

### Iteration 3: Advanced Parsing
- Better schema validation
- Unit normalization
- Date handling
- Reference ranges

### Iteration 4: FHIR Server Integration
- FHIR server client
- Bundle submission
- Error handling
- Retry logic

### Iteration 5: Multi-Patient Support
- Patient model
- Patient selection
- Access control

### Iteration 6: Production Readiness
- Heroku deployment config
- CI/CD automation
- Security hardening
- Performance optimization

---

## Labels for Issue Tracking

### Type Labels
- `epic` - High-level initiative
- `feature` - User-facing capability
- `task` - Implementation work
- `bug` - Something broken
- `enhancement` - Improvement to existing feature

### Component Labels
- `infrastructure` - Dev environment, CI/CD
- `ingestion` - PDF upload and storage
- `parsing` - LLM and text extraction
- `normalization` - Data cleaning
- `fhir` - FHIR resource generation
- `integration` - FHIR server interaction

### Priority Labels (for Kanban)
- `priority: critical` - Blocking MVP
- `priority: high` - Important for MVP
- `priority: medium` - Post-MVP polish
- `priority: low` - Nice to have

### Status Labels (for Kanban)
- `status: backlog` - Not started
- `status: ready` - Ready to work on
- `status: in-progress` - Active work
- `status: review` - Needs review
- `status: blocked` - Waiting on something

### Effort Labels
- `effort: small` - < 2 hours
- `effort: medium` - 2-4 hours
- `effort: large` - > 4 hours

---

## Dependencies Between Tasks

### Critical Path (MVP)
```
F1.1 (Project Structure)
  ↓
F1.2 (Dev Environment)
  ↓
F2.2 (Upload Endpoint) ← F3.1 (Text Extraction)
  ↓
F3.2 (LLM Schema) → F3.3 (OpenAI Integration)
  ↓
F5.1 (FHIR Library) → F5.2 (Observations)
  ↓
F5.5 (Bundle Creation)
```

### Parallel Workstreams
- **Infrastructure**: F1.3, F1.4, F1.5, F1.6 (can work in parallel)
- **Data modeling**: F2.1, F3.4, F4.4 (can prepare ahead)
- **Documentation**: F1.6, F3.2.3 (ongoing)
