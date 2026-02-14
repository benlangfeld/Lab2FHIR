#!/usr/bin/env python3
"""
Verification script for Lab2FHIR implementation.
Runs comprehensive checks to ensure all components are working correctly.
"""

import sys


def verify_imports():
    """Verify all required modules can be imported."""
    print("1. Verifying imports...")
    try:
        from lab2fhir import (
            Lab2FHIRPipeline,
            PDFExtractor,
            LabReportParser,
            FHIRConverter,
            FHIRClient,
            LabReport,
            LabResult,
            DateNormalizer,
            UnitNormalizer,
        )
        print("   ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False


def verify_schemas():
    """Verify Pydantic schemas work correctly."""
    print("\n2. Verifying schemas...")
    try:
        from lab2fhir import LabReport, LabResult

        # Create a valid lab report
        result = LabResult(
            test_name="Test",
            value="100",
            unit="mg/dL",
        )
        report = LabReport(
            patient_name="Test Patient",
            results=[result],
        )

        # Verify JSON serialization
        json_str = report.model_dump_json()
        assert "Test Patient" in json_str
        print("   ✓ Schemas validated successfully")
        return True
    except Exception as e:
        print(f"   ✗ Schema validation failed: {e}")
        return False


def verify_normalizers():
    """Verify unit and date normalizers."""
    print("\n3. Verifying normalizers...")
    try:
        from lab2fhir import UnitNormalizer, DateNormalizer

        # Test unit normalizer
        unit_norm = UnitNormalizer()
        assert unit_norm.normalize("mg/dl") == "mg/dL"
        assert unit_norm.normalize("mcg") == "ug"

        # Test date normalizer
        date_norm = DateNormalizer()
        assert date_norm.normalize("01/15/2024") == "2024-01-15"
        assert date_norm.normalize("2024-01-15") == "2024-01-15"

        print("   ✓ Normalizers working correctly")
        return True
    except Exception as e:
        print(f"   ✗ Normalizer test failed: {e}")
        return False


def verify_fhir_conversion():
    """Verify FHIR conversion works."""
    print("\n4. Verifying FHIR conversion...")
    try:
        from lab2fhir import FHIRConverter, LabReport, LabResult

        # Create test data
        report = LabReport(
            patient_name="Test Patient",
            patient_id="TEST123",
            collection_date="2024-01-15T10:00:00",
            results=[
                LabResult(test_name="Glucose", value="95", unit="mg/dL"),
            ],
        )

        # Convert to FHIR
        converter = FHIRConverter()
        bundle = converter.convert_to_bundle(report, "VGVzdA==", "test.pdf")

        # Verify bundle
        assert bundle.type == "transaction"
        assert bundle.entry is not None
        assert len(bundle.entry) >= 3  # DocumentRef, DiagnosticReport, at least 1 Observation

        # Verify JSON export
        json_str = converter.bundle_to_json(bundle)
        assert len(json_str) > 0
        assert "Test Patient" in json_str

        print(f"   ✓ FHIR conversion successful ({len(bundle.entry)} resources created)")
        return True
    except Exception as e:
        print(f"   ✗ FHIR conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_pdf_extractor():
    """Verify PDF extractor initializes correctly."""
    print("\n5. Verifying PDF extractor...")
    try:
        from lab2fhir import PDFExtractor

        extractor = PDFExtractor()
        # Just verify it can be instantiated
        print("   ✓ PDF extractor initialized")
        return True
    except Exception as e:
        print(f"   ✗ PDF extractor failed: {e}")
        return False


def verify_cli():
    """Verify CLI can be invoked."""
    print("\n6. Verifying CLI...")
    try:
        import subprocess
        result = subprocess.run(
            ["lab2fhir", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and "Lab2FHIR" in result.stdout:
            print("   ✓ CLI working correctly")
            return True
        else:
            print(f"   ✗ CLI failed with code {result.returncode}")
            return False
    except Exception as e:
        print(f"   ✗ CLI test failed: {e}")
        return False


def verify_tests():
    """Verify tests can run."""
    print("\n7. Verifying tests...")
    try:
        import subprocess
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            # Count passed tests
            passed = result.stdout.count(" PASSED")
            print(f"   ✓ All tests passed ({passed} tests)")
            return True
        else:
            print(f"   ✗ Tests failed")
            print(result.stdout[-500:])  # Show last 500 chars
            return False
    except Exception as e:
        print(f"   ✗ Test run failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "Lab2FHIR Verification" + " " * 22 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    checks = [
        verify_imports,
        verify_schemas,
        verify_normalizers,
        verify_fhir_conversion,
        verify_pdf_extractor,
        verify_cli,
        verify_tests,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"   ✗ Check failed with exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All verification checks passed!")
        print("  Lab2FHIR is ready to use.")
        return 0
    else:
        print(f"\n✗ {total - passed} verification check(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
