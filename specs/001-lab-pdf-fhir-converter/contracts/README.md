# API Contracts - Lab2FHIR

This directory contains the API contracts and data schemas for the Lab2FHIR system.

## Files

### `api.yaml`
OpenAPI 3.0 specification defining all REST API endpoints, request/response schemas, and examples.

**Endpoint Groups:**
- **Patient Management** (`/api/patients`)
  - Create patient profiles
  - List and retrieve patient details
  
- **PDF Processing** (`/api/uploads`)
  - Upload lab PDF reports
  - Track processing status
  - List upload history with filtering
  
- **Intermediate Representation** (`/api/uploads/{id}/intermediate`)
  - Retrieve extracted lab data
  - Edit and correct parsing errors
  - Version tracking for audit trail
  
- **FHIR Operations** (`/api/uploads/{id}/generate-fhir`, `/api/uploads/{id}/bundle`)
  - Generate FHIR R4 bundles
  - Download FHIR bundles as JSON/XML

**Key Features:**
- Complete request/response schemas with validation rules
- Comprehensive examples for all endpoints
- Error response definitions
- Processing status enumeration
- Authentication placeholder for future implementation

### `intermediate-schema.json`
JSON Schema (Draft 2020-12) defining the validated intermediate representation structure.

**Purpose:**
- Serves as the contract between LLM parsing and FHIR generation
- Enables schema validation of extracted data
- Provides clear structure for manual editing
- Supports audit trail with versioning

**Schema Structure:**
```json
{
  "lab_metadata": {
    "lab_name": "string",
    "lab_address": "string",
    "lab_phone": "string",
    "clia_number": "string"
  },
  "report_id": "string",
  "accession_number": "string",
  "collection_date": "date (ISO 8601)",
  "result_date": "date",
  "report_date": "date",
  "analytes": [
    {
      "analyte_name": "string (required)",
      "analyte_code": "string (LOINC)",
      "value": "string (required)",
      "value_type": "numeric | qualitative | operator",
      "operator": "< | > | <= | >=",
      "unit": "string",
      "reference_range": "string",
      "flag": "H | L | A | C",
      "notes": "string"
    }
  ],
  "specimen_type": "string",
  "specimen_id": "string",
  "ordering_provider": "string",
  "clinical_info": "string"
}
```

**Validation Rules:**
- `collection_date` is required and must be in ISO 8601 format (YYYY-MM-DD)
- At least one analyte must be present
- Numeric values should have units
- Operator values must include an operator field
- CLIA numbers follow format: `##X#######` (2 digits, 1 letter, 7 digits)

## Usage

### Viewing OpenAPI Specification

**With Swagger UI:**
```bash
# Run local Swagger UI
docker run -p 8080:8080 -e SWAGGER_JSON=/contracts/api.yaml \
  -v $(pwd):/contracts swaggerapi/swagger-ui
```

**With Redoc:**
```bash
# Run local Redoc
npx @redocly/cli preview-docs contracts/api.yaml
```

**Online:**
- Upload `api.yaml` to [Swagger Editor](https://editor.swagger.io/)
- Upload to [Stoplight Studio](https://stoplight.io/)

### Validating Intermediate JSON

**Using ajv-cli:**
```bash
npm install -g ajv-cli
ajv validate -s intermediate-schema.json -d sample-intermediate.json
```

**Using Python (jsonschema):**
```python
import json
from jsonschema import validate

with open('intermediate-schema.json') as f:
    schema = json.load(f)

with open('sample-data.json') as f:
    data = json.load(f)

validate(instance=data, schema=schema)
```

### Code Generation

**FastAPI Models (Python):**
```bash
# Install datamodel-code-generator
pip install datamodel-code-generator

# Generate Pydantic models from OpenAPI
datamodel-codegen --input api.yaml --output models.py
```

**TypeScript Types (Frontend):**
```bash
# Install openapi-typescript
npm install -g openapi-typescript

# Generate TypeScript types
openapi-typescript api.yaml --output api-types.ts
```

## Processing Workflow

The API supports the following processing workflow:

```
1. POST /api/patients
   └─> Create patient profile
   
2. POST /api/uploads (with patient_id)
   └─> Upload PDF (status: uploaded)
   └─> Text extraction begins (status: extracting)
   └─> LLM parsing begins (status: parsing)
   └─> Ready for review (status: review_pending)
   
3. GET /api/uploads/{id}/intermediate
   └─> Retrieve extracted data for review
   
4. (Optional) PUT /api/uploads/{id}/intermediate
   └─> Edit and correct parsing errors (status: editing)
   └─> Validation (status: validating)
   
5. POST /api/uploads/{id}/generate-fhir
   └─> Generate FHIR Bundle (status: generating_fhir)
   └─> Complete (status: completed)
   
6. GET /api/uploads/{id}/bundle
   └─> Download FHIR Bundle JSON file
```

## Status Transitions

Upload processing follows these state transitions:

```
uploaded → extracting → parsing → review_pending 
  → [editing → validating] → generating_fhir → completed
                                                    ↓
                                         regenerating_fhir
```

At any stage, the status can transition to `failed` with an `error_message`.

## Examples

See the `examples/` directory for:
- Sample intermediate JSON representations
- Example FHIR bundles
- cURL commands for API testing
- Postman collection

## Validation

Both contracts are validated against their respective specifications:

**OpenAPI:**
- Validated with [Spectral](https://stoplight.io/open-source/spectral)
- Follows OpenAPI 3.0.3 specification
- Includes all required components

**JSON Schema:**
- Validated with [AJV](https://ajv.js.org/)
- Follows JSON Schema Draft 2020-12
- Includes comprehensive examples

## Related Documentation

- Feature Specification: `../spec.md`
- Data Model: `../data-model.md`
- Implementation Plan: `../plan.md`

## Version

**API Version:** 1.0.0  
**Schema Version:** 1.0.0  
**Last Updated:** 2024-02-14
