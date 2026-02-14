# Lab2FHIR

Unlock structured insights from your lab reports

## Overview

Lab2FHIR is a Python service that converts text-based lab PDF reports into FHIR R4 resources. It extracts text from PDFs, uses OpenAI's Structured Outputs to parse results into a standardized JSON schema, validates and normalizes units and dates, and converts everything to FHIR R4 transaction Bundles that can be posted to any FHIR server.

## Features

- **PDF Text Extraction**: Automatically extracts text from lab report PDFs
- **AI-Powered Parsing**: Uses OpenAI Structured Outputs for accurate data extraction
- **Unit Normalization**: Standardizes lab test units to UCUM format
- **Date Validation**: Normalizes dates to ISO 8601 format
- **FHIR R4 Conversion**: Creates complete transaction Bundles with:
  - DocumentReference (with embedded base64 PDF)
  - DiagnosticReport
  - Observation resources for each lab result
- **FHIR Server Integration**: POST directly to any FHIR server (e.g., Fasten)

## Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Access to a FHIR R4 server (optional for testing)

### Install from source

```bash
git clone https://github.com/benlangfeld/Lab2FHIR.git
cd Lab2FHIR
pip install -e .
```

### Install dependencies for development

```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in your project directory:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# FHIR Server Configuration
FHIR_SERVER_URL=http://localhost:8080/fhir

# Optional: FHIR Server Authentication
FHIR_SERVER_AUTH_TOKEN=your-token-here
```

Or copy the example file:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Usage

### Command Line Interface

Process a lab report PDF:

```bash
lab2fhir process lab_report.pdf
```

Save intermediate JSON output:

```bash
lab2fhir process lab_report.pdf --output-json report.json
```

Save FHIR bundle output:

```bash
lab2fhir process lab_report.pdf --output-fhir bundle.json
```

Process without posting to FHIR server:

```bash
lab2fhir process lab_report.pdf --no-post
```

Test FHIR server connection:

```bash
lab2fhir test-connection
```

### Python API

```python
from lab2fhir import Lab2FHIRPipeline

# Initialize the pipeline
pipeline = Lab2FHIRPipeline(
    openai_api_key="your-key",
    fhir_server_url="http://localhost:8080/fhir"
)

# Process a PDF
result = pipeline.process_pdf(
    pdf_path="lab_report.pdf",
    output_json_path="report.json",
    output_fhir_path="bundle.json",
    post_to_server=True
)

print(f"Created {result['resource_count']} FHIR resources")
```

### Individual Components

You can also use individual components:

```python
from lab2fhir import PDFExtractor, LabReportParser, FHIRConverter

# Extract text from PDF
extractor = PDFExtractor()
text, pdf_base64 = extractor.extract_all("lab_report.pdf")

# Parse with OpenAI
parser = LabReportParser(api_key="your-key")
lab_report = parser.parse(text)

# Convert to FHIR
converter = FHIRConverter()
fhir_bundle = converter.convert_to_bundle(lab_report, pdf_base64)
```

## Architecture

The Lab2FHIR pipeline consists of several modular components:

1. **PDFExtractor** (`pdf_extractor.py`)
   - Extracts text content from PDF files
   - Encodes PDF as base64 for embedding

2. **LabReportParser** (`parser.py`)
   - Uses OpenAI Structured Outputs API
   - Parses text into intermediate JSON schema

3. **Normalizers** (`normalizers.py`)
   - `UnitNormalizer`: Standardizes lab units to UCUM format
   - `DateNormalizer`: Validates and normalizes dates to ISO 8601

4. **FHIRConverter** (`fhir_converter.py`)
   - Converts parsed data to FHIR R4 resources
   - Creates transaction Bundles with DocumentReference, DiagnosticReport, and Observation

5. **FHIRClient** (`fhir_client.py`)
   - POSTs transaction Bundles to FHIR servers
   - Handles authentication and error responses

6. **Pipeline** (`pipeline.py`)
   - Orchestrates the complete workflow
   - Manages intermediate outputs

## Intermediate JSON Schema

Lab2FHIR uses a strict intermediate schema defined with Pydantic:

```json
{
  "patient_name": "John Doe",
  "patient_id": "MRN12345",
  "date_of_birth": "1980-01-15",
  "collection_date": "2024-01-20T09:30:00",
  "report_date": "2024-01-20T14:00:00",
  "ordering_provider": "Dr. Jane Smith",
  "lab_name": "ABC Laboratory",
  "specimen_type": "Blood",
  "results": [
    {
      "test_name": "Glucose",
      "value": "95",
      "unit": "mg/dL",
      "reference_range": "70-100 mg/dL",
      "abnormal_flag": null
    },
    {
      "test_name": "Hemoglobin",
      "value": "15.2",
      "unit": "g/dL",
      "reference_range": "13.5-17.5 g/dL",
      "abnormal_flag": null
    }
  ],
  "notes": "All results within normal limits"
}
```

## FHIR R4 Resources

Lab2FHIR creates the following FHIR R4 resources:

- **DocumentReference**: Contains the original PDF as base64
- **DiagnosticReport**: Summary report linking to all observations
- **Observation**: One resource per lab test result with:
  - Test name and code
  - Numeric or string value
  - Reference range
  - Interpretation (High/Low/Abnormal flags)
  - Specimen information

All resources are bundled in a transaction Bundle for atomic posting to the FHIR server.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
ruff check src/
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issue tracker.
