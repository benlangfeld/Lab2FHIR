#!/usr/bin/env python3
"""
Example script demonstrating Lab2FHIR usage.
This example shows how to use the components individually and as a pipeline.
"""

import os
from lab2fhir import (
    Lab2FHIRPipeline,
    PDFExtractor,
    LabReportParser,
    FHIRConverter,
    FHIRClient,
    LabReport,
    LabResult,
)


def example_with_pipeline():
    """Example using the complete pipeline."""
    print("=" * 60)
    print("Example 1: Using the Complete Pipeline")
    print("=" * 60)

    # Set environment variables (normally in .env file)
    # os.environ["OPENAI_API_KEY"] = "your-api-key"
    # os.environ["FHIR_SERVER_URL"] = "http://localhost:8080/fhir"

    # Initialize the pipeline (requires API keys)
    # pipeline = Lab2FHIRPipeline()

    # Process a PDF (requires OpenAI API key and FHIR server)
    # result = pipeline.process_pdf(
    #     pdf_path="path/to/lab_report.pdf",
    #     output_json_path="output/report.json",
    #     output_fhir_path="output/bundle.json",
    #     post_to_server=True,
    # )
    #
    # print(f"Created {result['resource_count']} FHIR resources")
    # print(f"Bundle ID: {result['fhir_bundle_id']}")

    print("\nUsage:")
    print("  pipeline = Lab2FHIRPipeline()")
    print("  result = pipeline.process_pdf('lab_report.pdf')")
    print("\nNote: Requires OPENAI_API_KEY and FHIR_SERVER_URL")
    print("(See .env.example for configuration)")
    print()


def example_with_individual_components():
    """Example using individual components."""
    print("=" * 60)
    print("Example 2: Using Individual Components")
    print("=" * 60)

    # 1. Extract text from PDF
    print("\n1. PDF Text Extraction")
    print("-" * 40)
    extractor = PDFExtractor()
    # text, pdf_base64 = extractor.extract_all("path/to/lab_report.pdf")
    # print(f"Extracted {len(text)} characters")
    print("PDFExtractor initialized (requires actual PDF file)")

    # 2. Parse with OpenAI
    print("\n2. OpenAI Parsing")
    print("-" * 40)
    # parser = LabReportParser(api_key="your-key")
    # lab_report = parser.parse(text)
    # print(f"Parsed {len(lab_report.results)} lab results")
    print("LabReportParser ready (requires OpenAI API key)")

    # 3. Convert to FHIR
    print("\n3. FHIR Conversion")
    print("-" * 40)
    converter = FHIRConverter()

    # Create a sample lab report
    sample_report = LabReport(
        patient_name="John Doe",
        patient_id="MRN12345",
        collection_date="2024-01-20T09:30:00",
        results=[
            LabResult(test_name="Glucose", value="95", unit="mg/dL"),
            LabResult(test_name="Hemoglobin", value="15.2", unit="g/dL"),
        ],
    )

    # Convert to FHIR Bundle
    mock_pdf = "VGVzdCBQREY="  # Mock base64 PDF
    bundle = converter.convert_to_bundle(sample_report, mock_pdf)
    print(f"✓ Created FHIR Bundle with {len(bundle.entry)} entries")
    print(f"✓ Bundle ID: {bundle.id}")

    # Export to JSON
    bundle_json = converter.bundle_to_json(bundle)
    print(f"✓ Exported to JSON ({len(bundle_json)} bytes)")

    # 4. Post to FHIR server
    print("\n4. FHIR Server Client")
    print("-" * 40)
    # client = FHIRClient(server_url="http://localhost:8080/fhir")
    # response = client.post_bundle(bundle)
    # print("Posted to FHIR server successfully")
    print("FHIRClient ready (requires FHIR server URL)")
    print()


def example_normalizers():
    """Example using normalizers."""
    print("=" * 60)
    print("Example 3: Unit and Date Normalization")
    print("=" * 60)

    from lab2fhir import UnitNormalizer, DateNormalizer

    # Unit normalization
    print("\nUnit Normalization:")
    print("-" * 40)
    unit_normalizer = UnitNormalizer()

    units = ["mg/dl", "g/dl", "mmol/l", "mcg", "ml"]
    for unit in units:
        normalized = unit_normalizer.normalize(unit)
        print(f"  {unit:10s} → {normalized}")

    # Date normalization
    print("\nDate Normalization:")
    print("-" * 40)
    date_normalizer = DateNormalizer()

    dates = [
        "01/15/2024",
        "2024-01-15",
        "January 15, 2024",
        "01/15/2024 10:30",
    ]
    for date in dates:
        normalized = date_normalizer.normalize(date)
        print(f"  {date:20s} → {normalized}")
    print()


def example_json_schema():
    """Example showing the intermediate JSON schema."""
    print("=" * 60)
    print("Example 4: Intermediate JSON Schema")
    print("=" * 60)

    # Create a lab report
    lab_report = LabReport(
        patient_name="Jane Smith",
        patient_id="MRN67890",
        date_of_birth="1985-03-22",
        collection_date="2024-01-25T08:00:00",
        report_date="2024-01-25T12:00:00",
        ordering_provider="Dr. Robert Johnson",
        lab_name="City Laboratory",
        specimen_type="Blood",
        results=[
            LabResult(
                test_name="Glucose",
                value="92",
                unit="mg/dL",
                reference_range="70-100 mg/dL",
                abnormal_flag=None,
            ),
            LabResult(
                test_name="Cholesterol",
                value="220",
                unit="mg/dL",
                reference_range="<200 mg/dL",
                abnormal_flag="H",
            ),
        ],
        notes="Cholesterol slightly elevated",
    )

    # Export to JSON
    json_output = lab_report.model_dump_json(indent=2)
    print("\nIntermediate JSON Schema:")
    print("-" * 40)
    print(json_output)
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 16 + "Lab2FHIR Usage Examples" + " " * 19 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    # Run examples
    example_with_pipeline()
    example_with_individual_components()
    example_normalizers()
    example_json_schema()

    print("=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)
    print("\nFor more information, see the README.md file.")
