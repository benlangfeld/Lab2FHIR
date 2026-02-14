#!/bin/bash
# GitHub Issues Creation Script for Lab2FHIR
# Prerequisites: GitHub CLI (gh) installed and authenticated
# Usage: ./github-issues.sh

set -e

REPO="benlangfeld/Lab2FHIR"

echo "Creating labels..."

# Type labels
gh label create "epic" --color "8B5CF6" --description "High-level initiative spanning multiple features" --repo $REPO || true
gh label create "feature" --color "3B82F6" --description "User-facing capability" --repo $REPO || true
gh label create "task" --color "10B981" --description "Implementation work" --repo $REPO || true
gh label create "bug" --color "EF4444" --description "Something broken" --repo $REPO || true
gh label create "enhancement" --color "F59E0B" --description "Improvement to existing feature" --repo $REPO || true

# Component labels
gh label create "infrastructure" --color "6366F1" --description "Dev environment, CI/CD" --repo $REPO || true
gh label create "ingestion" --color "EC4899" --description "PDF upload and storage" --repo $REPO || true
gh label create "parsing" --color "14B8A6" --description "LLM and text extraction" --repo $REPO || true
gh label create "normalization" --color "F97316" --description "Data cleaning and validation" --repo $REPO || true
gh label create "fhir" --color "06B6D4" --description "FHIR resource generation" --repo $REPO || true
gh label create "integration" --color "8B5CF6" --description "FHIR server interaction" --repo $REPO || true

# Priority labels
gh label create "priority: critical" --color "DC2626" --description "Blocking MVP" --repo $REPO || true
gh label create "priority: high" --color "F59E0B" --description "Important for MVP" --repo $REPO || true
gh label create "priority: medium" --color "3B82F6" --description "Post-MVP polish" --repo $REPO || true
gh label create "priority: low" --color "9CA3AF" --description "Nice to have" --repo $REPO || true

# Status labels
gh label create "status: backlog" --color "D1D5DB" --description "Not started" --repo $REPO || true
gh label create "status: ready" --color "3B82F6" --description "Ready to work on" --repo $REPO || true
gh label create "status: in-progress" --color "FBBF24" --description "Active work" --repo $REPO || true
gh label create "status: review" --color "8B5CF6" --description "Needs review" --repo $REPO || true
gh label create "status: blocked" --color "EF4444" --description "Waiting on something" --repo $REPO || true

# Effort labels
gh label create "effort: small" --color "BBF7D0" --description "< 2 hours" --repo $REPO || true
gh label create "effort: medium" --color "FDE68A" --description "2-4 hours" --repo $REPO || true
gh label create "effort: large" --color "FECACA" --description "> 4 hours" --repo $REPO || true

echo "Labels created successfully!"
echo ""
echo "Creating Epic issues..."

# Epic 1: Project Infrastructure & Development Environment
EPIC1=$(gh issue create \
  --repo $REPO \
  --title "Epic 1: Project Infrastructure & Development Environment" \
  --label "epic,infrastructure,priority: critical" \
  --body "**Goal**: Set up a production-ready Python development environment with CI/CD

## Features
- F1.1: Python Project Structure
- F1.2: Development Environment
- F1.3: Code Quality & Linting
- F1.4: Testing Infrastructure
- F1.5: CI/CD Pipeline
- F1.6: Documentation

## Success Criteria
- Python project runs in GitHub Codespaces
- CI/CD pipeline tests and lints code
- Development environment is reproducible
- Documentation exists for contributors" | grep -oP '\d+$')

echo "Created Epic 1: #$EPIC1"

# Epic 2: PDF Ingestion Layer
EPIC2=$(gh issue create \
  --repo $REPO \
  --title "Epic 2: PDF Ingestion Layer" \
  --label "epic,ingestion,priority: critical" \
  --body "**Goal**: Accept PDF uploads, deduplicate, and prepare for processing

## Features
- F2.1: Storage Backend
- F2.2: PDF Upload Handler
- F2.3: Document Management
- F2.4: Multi-Patient Support

## Success Criteria
- PDFs can be uploaded via API
- Files are deduplicated by hash
- Documents are associated with patients
- Storage is persistent" | grep -oP '\d+$')

echo "Created Epic 2: #$EPIC2"

# Epic 3: LLM Parsing Layer
EPIC3=$(gh issue create \
  --repo $REPO \
  --title "Epic 3: LLM Parsing Layer" \
  --label "epic,parsing,priority: critical" \
  --body "**Goal**: Extract structured lab data from PDF text using LLM with strict schema

## Features
- F3.1: PDF Text Extraction
- F3.2: LLM Schema Design
- F3.3: OpenAI Integration
- F3.4: Parse Result Storage
- F3.5: Quality Assurance

## Success Criteria
- Text extracted from PDFs
- LLM returns structured JSON
- Schema is validated with Pydantic
- Parse results are stored" | grep -oP '\d+$')

echo "Created Epic 3: #$EPIC3"

# Epic 4: Normalization & Validation Layer
EPIC4=$(gh issue create \
  --repo $REPO \
  --title "Epic 4: Normalization & Validation Layer" \
  --label "epic,normalization,priority: high" \
  --body "**Goal**: Clean, validate, and normalize extracted lab data

## Features
- F4.1: Unit Normalization
- F4.2: Date Normalization
- F4.3: Value Validation
- F4.4: Analyte Name Canonicalization
- F4.5: Data Quality Checks

## Success Criteria
- Units are standardized
- Dates are normalized
- Values are validated
- Analyte names are canonical" | grep -oP '\d+$')

echo "Created Epic 4: #$EPIC4"

# Epic 5: FHIR Generation Layer
EPIC5=$(gh issue create \
  --repo $REPO \
  --title "Epic 5: FHIR Generation Layer" \
  --label "epic,fhir,priority: critical" \
  --body "**Goal**: Convert normalized data into valid FHIR R4 resources

## Features
- F5.1: FHIR Library Integration
- F5.2: Observation Generation
- F5.3: DiagnosticReport Generation
- F5.4: DocumentReference Generation
- F5.5: Bundle Creation
- F5.6: Patient Resource Handling

## Success Criteria
- FHIR resources are valid R4
- Observations contain lab values
- DiagnosticReport links observations
- Bundle is a valid transaction" | grep -oP '\d+$')

echo "Created Epic 5: #$EPIC5"

# Epic 6: FHIR Store Integration
EPIC6=$(gh issue create \
  --repo $REPO \
  --title "Epic 6: FHIR Store Integration" \
  --label "epic,integration,priority: high" \
  --body "**Goal**: Push FHIR bundles to FHIR server with retry and status tracking

## Features
- F6.1: FHIR Server Client
- F6.2: Bundle Submission
- F6.3: Error Handling & Retry
- F6.4: Status Tracking
- F6.5: Deduplication Logic

## Success Criteria
- Bundles POST to FHIR server
- Errors are handled gracefully
- Failed submissions can be retried
- Status is tracked and visible" | grep -oP '\d+$')

echo "Created Epic 6: #$EPIC6"

echo ""
echo "Creating Feature and Task issues..."

# Feature 1.1: Python Project Structure
F11=$(gh issue create \
  --repo $REPO \
  --title "F1.1: Python Project Structure" \
  --label "feature,infrastructure,priority: critical,effort: medium" \
  --body "Initialize a modern Python project with proper structure.

## Tasks
- [ ] Task 1.1.1: Initialize Python project with pyproject.toml
- [ ] Task 1.1.2: Set up package structure (src/lab2fhir/)
- [ ] Task 1.1.3: Configure Poetry for dependency management
- [ ] Task 1.1.4: Add .gitignore for Python projects

## Acceptance Criteria
- pyproject.toml exists with project metadata
- src/lab2fhir/ package structure is created
- Poetry is configured and working
- .gitignore excludes Python artifacts

Related to #$EPIC1" | grep -oP '\d+$')

# Individual tasks for Feature 1.1
gh issue create --repo $REPO --title "Task 1.1.1: Initialize Python project with pyproject.toml" \
  --label "task,infrastructure,priority: critical,effort: small" \
  --body "Create pyproject.toml with project metadata, dependencies, and build configuration.

Related to #$F11, #$EPIC1" > /dev/null

gh issue create --repo $REPO --title "Task 1.1.2: Set up package structure (src/lab2fhir/)" \
  --label "task,infrastructure,priority: critical,effort: small" \
  --body "Create src/ layout with lab2fhir package and __init__.py files.

Related to #$F11, #$EPIC1" > /dev/null

gh issue create --repo $REPO --title "Task 1.1.3: Configure Poetry for dependency management" \
  --label "task,infrastructure,priority: critical,effort: small" \
  --body "Set up Poetry for dependency management and virtual environment.

Related to #$F11, #$EPIC1" > /dev/null

gh issue create --repo $REPO --title "Task 1.1.4: Add .gitignore for Python projects" \
  --label "task,infrastructure,priority: critical,effort: small" \
  --body "Add comprehensive .gitignore for Python, IDEs, and OS files.

Related to #$F11, #$EPIC1" > /dev/null

# Feature 1.2: Development Environment
F12=$(gh issue create \
  --repo $REPO \
  --title "F1.2: Development Environment" \
  --label "feature,infrastructure,priority: critical,effort: medium" \
  --body "Set up GitHub Codespaces development environment.

## Tasks
- [ ] Task 1.2.1: Create devcontainer.json for GitHub Codespaces
- [ ] Task 1.2.2: Configure VS Code settings and extensions
- [ ] Task 1.2.3: Add development dependencies (pytest, black, ruff, mypy)
- [ ] Task 1.2.4: Create Makefile with common commands

## Acceptance Criteria
- Codespace starts successfully
- VS Code has Python extensions
- Development tools are installed
- Makefile provides common commands (test, lint, format)

Related to #$EPIC1" | grep -oP '\d+$')

gh issue create --repo $REPO --title "Task 1.2.1: Create devcontainer.json for GitHub Codespaces" \
  --label "task,infrastructure,priority: critical,effort: medium" \
  --body "Configure devcontainer.json with Python, PostgreSQL, and necessary tools.

Related to #$F12, #$EPIC1" > /dev/null

gh issue create --repo $REPO --title "Task 1.2.2: Configure VS Code settings and extensions" \
  --label "task,infrastructure,priority: critical,effort: small" \
  --body "Add .vscode/settings.json and recommended extensions for Python development.

Related to #$F12, #$EPIC1" > /dev/null

gh issue create --repo $REPO --title "Task 1.2.3: Add development dependencies" \
  --label "task,infrastructure,priority: critical,effort: small" \
  --body "Add pytest, ruff, mypy, and other development tools to pyproject.toml.

Related to #$F12, #$EPIC1" > /dev/null

gh issue create --repo $REPO --title "Task 1.2.4: Create Makefile with common commands" \
  --label "task,infrastructure,priority: critical,effort: small" \
  --body "Create Makefile with targets: test, lint, format, run, clean.

Related to #$F12, #$EPIC1" > /dev/null

# Feature 1.3: Code Quality & Linting
gh issue create --repo $REPO --title "F1.3: Code Quality & Linting" \
  --label "feature,infrastructure,priority: high,effort: medium" \
  --body "Configure linting and type checking tools.

## Tasks
- [ ] Task 1.3.1: Configure Ruff for linting and formatting
- [ ] Task 1.3.2: Configure mypy for type checking
- [ ] Task 1.3.3: Set up pre-commit hooks
- [ ] Task 1.3.4: Add code quality checks to CI

Related to #$EPIC1" > /dev/null

# Feature 1.4: Testing Infrastructure
gh issue create --repo $REPO --title "F1.4: Testing Infrastructure" \
  --label "feature,infrastructure,priority: high,effort: medium" \
  --body "Set up pytest with coverage reporting.

## Tasks
- [ ] Task 1.4.1: Set up pytest with coverage reporting
- [ ] Task 1.4.2: Create test fixtures for sample PDFs
- [ ] Task 1.4.3: Add test utilities and helpers
- [ ] Task 1.4.4: Configure coverage thresholds

Related to #$EPIC1" > /dev/null

# Feature 1.5: CI/CD Pipeline
gh issue create --repo $REPO --title "F1.5: CI/CD Pipeline" \
  --label "feature,infrastructure,priority: high,effort: large" \
  --body "Create GitHub Actions workflows for automated testing and deployment.

## Tasks
- [ ] Task 1.5.1: Create GitHub Actions workflow for tests
- [ ] Task 1.5.2: Create GitHub Actions workflow for linting
- [ ] Task 1.5.3: Add security scanning (Dependabot, CodeQL)
- [ ] Task 1.5.4: Set up automated dependency updates

Related to #$EPIC1" > /dev/null

# Feature 1.6: Documentation
gh issue create --repo $REPO --title "F1.6: Documentation" \
  --label "feature,infrastructure,priority: medium,effort: medium" \
  --body "Create project documentation.

## Tasks
- [ ] Task 1.6.1: Create CONTRIBUTING.md
- [ ] Task 1.6.2: Create architecture documentation
- [ ] Task 1.6.3: Set up API documentation with Sphinx
- [ ] Task 1.6.4: Add inline code documentation standards

Related to #$EPIC1" > /dev/null

# Feature 2.1: Storage Backend
gh issue create --repo $REPO --title "F2.1: Storage Backend" \
  --label "feature,ingestion,priority: high,effort: large" \
  --body "Set up PostgreSQL database with SQLAlchemy ORM.

## Tasks
- [ ] Task 2.1.1: Set up PostgreSQL database schema
- [ ] Task 2.1.2: Create SQLAlchemy models for documents
- [ ] Task 2.1.3: Implement database migrations with Alembic
- [ ] Task 2.1.4: Add database connection pooling

Related to #$EPIC2" > /dev/null

# Feature 2.2: PDF Upload Handler
F22=$(gh issue create \
  --repo $REPO \
  --title "F2.2: PDF Upload Handler" \
  --label "feature,ingestion,priority: critical,effort: large" \
  --body "Create web API for PDF uploads.

## Tasks
- [ ] Task 2.2.1: Create Flask/FastAPI web application skeleton
- [ ] Task 2.2.2: Implement PDF upload endpoint
- [ ] Task 2.2.3: Add file validation (size, type, format)
- [ ] Task 2.2.4: Store uploaded PDFs (filesystem or blob storage)

## Acceptance Criteria
- API accepts PDF uploads
- Files are validated
- PDFs are stored persistently

Related to #$EPIC2" | grep -oP '\d+$')

gh issue create --repo $REPO --title "Task 2.2.1: Create Flask/FastAPI web application skeleton" \
  --label "task,ingestion,priority: critical,effort: medium" \
  --body "Set up basic Flask or FastAPI application with health check endpoint.

Related to #$F22, #$EPIC2" > /dev/null

gh issue create --repo $REPO --title "Task 2.2.2: Implement PDF upload endpoint" \
  --label "task,ingestion,priority: critical,effort: medium" \
  --body "Create POST /upload endpoint that accepts PDF files.

Related to #$F22, #$EPIC2" > /dev/null

# Feature 2.3: Document Management
gh issue create --repo $REPO --title "F2.3: Document Management" \
  --label "feature,ingestion,priority: high,effort: medium" \
  --body "Implement document deduplication and metadata storage.

## Tasks
- [ ] Task 2.3.1: Implement file hash calculation for deduplication
- [ ] Task 2.3.2: Create document metadata storage
- [ ] Task 2.3.3: Add patient/subject association logic
- [ ] Task 2.3.4: Implement document status tracking

Related to #$EPIC2" > /dev/null

# Feature 3.1: PDF Text Extraction
F31=$(gh issue create \
  --repo $REPO \
  --title "F3.1: PDF Text Extraction" \
  --label "feature,parsing,priority: critical,effort: medium" \
  --body "Extract text from PDF files.

## Tasks
- [ ] Task 3.1.1: Evaluate and select PDF parsing library
- [ ] Task 3.1.2: Implement text extraction pipeline
- [ ] Task 3.1.3: Handle multi-page PDFs
- [ ] Task 3.1.4: Add text quality validation

## Acceptance Criteria
- Text extracted from sample PDFs
- Multi-page documents handled
- Quality checks for extracted text

Related to #$EPIC3" | grep -oP '\d+$')

gh issue create --repo $REPO --title "Task 3.1.1: Evaluate and select PDF parsing library" \
  --label "task,parsing,priority: critical,effort: small" \
  --body "Research and select PDF library (PyPDF2, pdfplumber, pypdf, etc).

Related to #$F31, #$EPIC3" > /dev/null

gh issue create --repo $REPO --title "Task 3.1.2: Implement text extraction pipeline" \
  --label "task,parsing,priority: critical,effort: medium" \
  --body "Create function to extract text from PDF files.

Related to #$F31, #$EPIC3" > /dev/null

# Feature 3.2: LLM Schema Design
F32=$(gh issue create \
  --repo $REPO \
  --title "F3.2: LLM Schema Design" \
  --label "feature,parsing,priority: critical,effort: large" \
  --body "Define JSON schema for lab results.

## Tasks
- [ ] Task 3.2.1: Define intermediate JSON schema for lab results
- [ ] Task 3.2.2: Create Pydantic models for validation
- [ ] Task 3.2.3: Document schema with examples
- [ ] Task 3.2.4: Version schema for future changes

## Acceptance Criteria
- Schema covers lab metadata and results
- Pydantic models validate schema
- Documentation with examples exists

Related to #$EPIC3" | grep -oP '\d+$')

gh issue create --repo $REPO --title "Task 3.2.1: Define intermediate JSON schema for lab results" \
  --label "task,parsing,priority: critical,effort: medium" \
  --body "Design JSON schema that LLM will output with lab data structure.

Related to #$F32, #$EPIC3" > /dev/null

gh issue create --repo $REPO --title "Task 3.2.2: Create Pydantic models for validation" \
  --label "task,parsing,priority: critical,effort: medium" \
  --body "Implement Pydantic models matching the JSON schema.

Related to #$F32, #$EPIC3" > /dev/null

# Feature 3.3: OpenAI Integration
F33=$(gh issue create \
  --repo $REPO \
  --title "F3.3: OpenAI Integration" \
  --label "feature,parsing,priority: critical,effort: large" \
  --body "Integrate OpenAI API for structured parsing.

## Tasks
- [ ] Task 3.3.1: Set up OpenAI API client
- [ ] Task 3.3.2: Implement structured output with function calling
- [ ] Task 3.3.3: Create prompt templates for lab parsing
- [ ] Task 3.3.4: Add retry logic and error handling

## Acceptance Criteria
- OpenAI API successfully called
- Structured JSON returned
- Errors handled gracefully

Related to #$EPIC3" | grep -oP '\d+$')

gh issue create --repo $REPO --title "Task 3.3.1: Set up OpenAI API client" \
  --label "task,parsing,priority: critical,effort: small" \
  --body "Configure OpenAI Python client with API key from environment.

Related to #$F33, #$EPIC3" > /dev/null

gh issue create --repo $REPO --title "Task 3.3.2: Implement structured output with function calling" \
  --label "task,parsing,priority: critical,effort: large" \
  --body "Use OpenAI function calling or structured outputs to get JSON matching schema.

Related to #$F33, #$EPIC3" > /dev/null

gh issue create --repo $REPO --title "Task 3.3.3: Create prompt templates for lab parsing" \
  --label "task,parsing,priority: critical,effort: medium" \
  --body "Design prompts that instruct LLM to extract lab data from text.

Related to #$F33, #$EPIC3" > /dev/null

# Feature 3.4: Parse Result Storage
gh issue create --repo $REPO --title "F3.4: Parse Result Storage" \
  --label "feature,parsing,priority: medium,effort: medium" \
  --body "Store intermediate parse results in database.

## Tasks
- [ ] Task 3.4.1: Store intermediate JSON results in database
- [ ] Task 3.4.2: Link parsed results to source PDFs
- [ ] Task 3.4.3: Add parsing status and error tracking
- [ ] Task 3.4.4: Implement parse result versioning

Related to #$EPIC3" > /dev/null

# Feature 5.1: FHIR Library Integration
F51=$(gh issue create \
  --repo $REPO \
  --title "F5.1: FHIR Library Integration" \
  --label "feature,fhir,priority: critical,effort: medium" \
  --body "Integrate Python FHIR library.

## Tasks
- [ ] Task 5.1.1: Select and integrate FHIR library (fhir.resources)
- [ ] Task 5.1.2: Set up FHIR resource builders
- [ ] Task 5.1.3: Add FHIR validation
- [ ] Task 5.1.4: Configure FHIR resource profiles

## Acceptance Criteria
- fhir.resources library integrated
- Can create FHIR resources
- Resources validate against R4 spec

Related to #$EPIC5" | grep -oP '\d+$')

gh issue create --repo $REPO --title "Task 5.1.1: Select and integrate FHIR library (fhir.resources)" \
  --label "task,fhir,priority: critical,effort: small" \
  --body "Add fhir.resources library to dependencies and verify it works.

Related to #$F51, #$EPIC5" > /dev/null

gh issue create --repo $REPO --title "Task 5.1.2: Set up FHIR resource builders" \
  --label "task,fhir,priority: critical,effort: medium" \
  --body "Create helper functions to build FHIR resources from parsed data.

Related to #$F51, #$EPIC5" > /dev/null

# Feature 5.2: Observation Generation
F52=$(gh issue create \
  --repo $REPO \
  --title "F5.2: Observation Generation" \
  --label "feature,fhir,priority: critical,effort: large" \
  --body "Generate FHIR Observation resources from lab results.

## Tasks
- [ ] Task 5.2.1: Create Observation resources from analytes
- [ ] Task 5.2.2: Map values and units to FHIR structure
- [ ] Task 5.2.3: Add reference ranges to Observations
- [ ] Task 5.2.4: Implement observation identifiers for deduplication

## Acceptance Criteria
- Observations created for each analyte
- Values, units, and ranges properly mapped
- Valid FHIR R4 Observations

Related to #$EPIC5" | grep -oP '\d+$')

gh issue create --repo $REPO --title "Task 5.2.1: Create Observation resources from analytes" \
  --label "task,fhir,priority: critical,effort: medium" \
  --body "Build FHIR Observation for each lab test result.

Related to #$F52, #$EPIC5" > /dev/null

gh issue create --repo $REPO --title "Task 5.2.2: Map values and units to FHIR structure" \
  --label "task,fhir,priority: critical,effort: medium" \
  --body "Map numeric/qualitative values and units to FHIR valueQuantity/valueCodeableConcept.

Related to #$F52, #$EPIC5" > /dev/null

# Feature 5.5: Bundle Creation
F55=$(gh issue create \
  --repo $REPO \
  --title "F5.5: Bundle Creation" \
  --label "feature,fhir,priority: critical,effort: medium" \
  --body "Create FHIR transaction Bundle.

## Tasks
- [ ] Task 5.5.1: Create transaction Bundle
- [ ] Task 5.5.2: Include all resources in Bundle
- [ ] Task 5.5.3: Set Bundle identifiers
- [ ] Task 5.5.4: Validate complete Bundle

## Acceptance Criteria
- Bundle type is transaction
- All resources included
- Bundle validates successfully

Related to #$EPIC5" | grep -oP '\d+$')

gh issue create --repo $REPO --title "Task 5.5.1: Create transaction Bundle" \
  --label "task,fhir,priority: critical,effort: small" \
  --body "Create FHIR Bundle resource with type=transaction.

Related to #$F55, #$EPIC5" > /dev/null

gh issue create --repo $REPO --title "Task 5.5.2: Include all resources in Bundle" \
  --label "task,fhir,priority: critical,effort: medium" \
  --body "Add Observations, DiagnosticReport, DocumentReference to Bundle entries.

Related to #$F55, #$EPIC5" > /dev/null

echo ""
echo "✅ Successfully created GitHub issues!"
echo ""
echo "Next steps:"
echo "1. Visit https://github.com/$REPO/issues to see all created issues"
echo "2. Create a GitHub Project board and add these issues"
echo "3. Organize issues into Kanban columns: Backlog, Ready, In Progress, Review, Done"
echo ""
echo "MVP Priority Issues (start here):"
echo "- #$F11 - Python Project Structure"
echo "- #$F12 - Development Environment"
echo "- #$F22 - PDF Upload Handler"
echo "- #$F31 - PDF Text Extraction"
echo "- #$F32 - LLM Schema Design"
echo "- #$F33 - OpenAI Integration"
echo "- #$F51 - FHIR Library Integration"
echo "- #$F52 - Observation Generation"
echo "- #$F55 - Bundle Creation"
