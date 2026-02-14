#!/usr/bin/env python3
"""
Integration test script for Lab2FHIR.
Tests the complete workflow without requiring OpenAI API or FHIR server.
"""

import sys
from lab2fhir import (
    FHIRConverter,
    LabReport,
    LabResult,
    DateNormalizer,
    UnitNormalizer,
)


def test_integration():
    """Test the complete workflow with mock data."""
    print("Testing Lab2FHIR Integration...")
    print("=" * 60)

    # Create mock lab report data
    print("\n1. Creating mock lab report...")
    results = [
        LabResult(
            test_name="Glucose",
            value="95",
            unit="mg/dl",
            reference_range="70-100 mg/dL",
            abnormal_flag=None,
        ),
        LabResult(
            test_name="Hemoglobin",
            value="15.2",
            unit="g/dl",
            reference_range="13.5-17.5 g/dL",
            abnormal_flag=None,
        ),
        LabResult(
            test_name="LDL Cholesterol",
            value="110",
            unit="mg/dl",
            reference_range="<100 mg/dL",
            abnormal_flag="H",
        ),
    ]

    lab_report = LabReport(
        patient_name="John Doe",
        patient_id="MRN12345",
        date_of_birth="1980-01-15",
        collection_date="2024-01-20T09:30:00",
        report_date="2024-01-20T14:00:00",
        ordering_provider="Dr. Jane Smith",
        lab_name="ABC Laboratory",
        specimen_type="Blood",
        results=results,
        notes="Test report for integration testing",
    )
    print(f"   ✓ Created report with {len(results)} results")

    # Test normalizers
    print("\n2. Testing normalizers...")
    unit_normalizer = UnitNormalizer()
    date_normalizer = DateNormalizer()

    normalized_unit = unit_normalizer.normalize("mg/dl")
    print(f"   ✓ Unit normalization: mg/dl → {normalized_unit}")

    normalized_date = date_normalizer.normalize("01/20/2024")
    print(f"   ✓ Date normalization: 01/20/2024 → {normalized_date}")

    # Test FHIR conversion
    print("\n3. Converting to FHIR Bundle...")
    converter = FHIRConverter()

    # Create mock base64 PDF (empty for testing)
    mock_pdf_base64 = "VGhpcyBpcyBhIG1vY2sgUERG"  # "This is a mock PDF" in base64

    fhir_bundle = converter.convert_to_bundle(
        lab_report, mock_pdf_base64, "test_report.pdf"
    )
    print(f"   ✓ Bundle created with ID: {fhir_bundle.id}")
    print(f"   ✓ Bundle type: {fhir_bundle.type}")
    print(f"   ✓ Number of entries: {len(fhir_bundle.entry)}")

    # Verify bundle entries
    print("\n4. Verifying FHIR resources...")
    from fhir.resources.documentreference import DocumentReference
    from fhir.resources.diagnosticreport import DiagnosticReport
    from fhir.resources.observation import Observation
    
    entry_types = []
    for entry in fhir_bundle.entry:
        # Use isinstance to check resource type
        if isinstance(entry.resource, DocumentReference):
            resource_type = "DocumentReference"
        elif isinstance(entry.resource, DiagnosticReport):
            resource_type = "DiagnosticReport"
        elif isinstance(entry.resource, Observation):
            resource_type = "Observation"
        else:
            resource_type = type(entry.resource).__name__
        
        entry_types.append(resource_type)
        print(f"   ✓ {resource_type} (ID: {entry.resource.id})")

    expected_types = ["DocumentReference", "DiagnosticReport"] + ["Observation"] * len(
        results
    )
    assert len(entry_types) == len(expected_types), \
        f"Expected {len(expected_types)} resources, got {len(entry_types)}"
    print(f"\n   ✓ All {len(expected_types)} resources created successfully")

    # Test JSON export
    print("\n5. Testing JSON export...")
    bundle_json = converter.bundle_to_json(fhir_bundle)
    assert len(bundle_json) > 0, "Failed to export JSON"
    print(f"   ✓ Bundle JSON exported ({len(bundle_json)} bytes)")

    # Verify key data in JSON
    assert "John Doe" in bundle_json and "Glucose" in bundle_json, \
        "Missing expected data in JSON"
    print("   ✓ Patient name and test results present in JSON")

    print("\n" + "=" * 60)
    print("✓ All integration tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_integration()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
