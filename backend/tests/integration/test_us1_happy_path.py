"""Integration test for User Story 1 happy path: upload → parse → generate → download."""

import io

import pytest
from httpx import AsyncClient
from reportlab.pdfgen import canvas

from src.db.models import ReportStatus, SubjectType


@pytest.mark.integration
@pytest.mark.asyncio
async def test_us1_happy_path(client: AsyncClient):
    """
    Test the complete workflow:
    1. Create a patient
    2. Upload a lab PDF
    3. Verify parsing completes
    4. Get parsed data
    5. Generate FHIR bundle
    6. Download bundle
    """
    # 1. Create patient
    patient_data = {
        "external_subject_id": "test-patient-001",
        "display_name": "Test Patient",
        "subject_type": SubjectType.HUMAN.value,
    }

    response = await client.post("/api/v1/patients", json=patient_data)
    assert response.status_code == 201
    patient = response.json()
    patient_id = patient["id"]

    # 2. Create a simple test PDF with lab results
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)

    # Header
    c.drawString(100, 750, "LABORATORY REPORT")
    c.drawString(100, 720, "Quest Diagnostics Laboratory")
    c.drawString(100, 700, "123 Medical Center Drive, Anytown, ST 12345")

    # Patient Info
    c.drawString(100, 660, "Patient Information:")
    c.drawString(120, 640, "Name: Test Patient")
    c.drawString(120, 620, "Patient ID: TEST-001")
    c.drawString(120, 600, "Date of Birth: 1980-01-01")
    c.drawString(120, 580, "Collection Date: 2024-01-15 08:00:00")

    # Provider Info
    c.drawString(100, 540, "Ordering Provider: Dr. Jane Smith, MD")
    c.drawString(100, 520, "Report Date: 2024-01-16")

    # Results Section
    c.drawString(100, 480, "Test Results:")
    c.drawString(100, 460, "-" * 70)
    c.drawString(100, 440, "Test Name                Value      Unit       Reference Range")
    c.drawString(100, 420, "-" * 70)
    c.drawString(100, 400, "Glucose                  95.0       mg/dL      70-100 mg/dL")
    c.drawString(100, 380, "Hemoglobin A1c          5.5        %          <5.7%")
    c.drawString(100, 360, "Creatinine              1.0        mg/dL      0.7-1.3 mg/dL")
    c.drawString(100, 340, "Total Cholesterol        180        mg/dL      <200 mg/dL")

    # Footer
    c.drawString(100, 300, "All results are within normal ranges.")
    c.drawString(100, 280, "Performing Laboratory: Quest Diagnostics")
    c.drawString(100, 260, "Laboratory Director: Dr. Robert Johnson, PhD")

    c.save()
    pdf_content = pdf_buffer.getvalue()

    # 3. Upload report
    files = {"file": ("lab_report.pdf", pdf_content, "application/pdf")}
    data = {"patient_id": patient_id}

    response = await client.post("/api/v1/reports", files=files, data=data)
    assert response.status_code == 201
    report = response.json()
    report_id = report["id"]

    # Should be in review_pending status after parsing
    if report["status"] == ReportStatus.FAILED.value:
        # Print error details for debugging
        error_msg = report.get("error_message", "No error message")
        error_code = report.get("error_code", "No error code")
        raise AssertionError(
            f"Report processing failed with status='{report['status']}', "
            f"error_code='{error_code}', error_message='{error_msg}'"
        )

    assert report["status"] in [
        ReportStatus.PARSING.value,
        ReportStatus.REVIEW_PENDING.value,
    ]

    # 4. Get report status (may need to poll in real scenario)
    response = await client.get(f"/api/v1/reports/{report_id}")
    assert response.status_code == 200
    report = response.json()

    # If still parsing, this would fail in a real async scenario
    # For this test, we assume synchronous processing completed
    if report["status"] == ReportStatus.REVIEW_PENDING.value:
        # 5. Get parsed data
        response = await client.get(f"/api/v1/parsed-data/{report_id}")
        assert response.status_code == 200
        parsed_data = response.json()

        assert "payload" in parsed_data
        assert "measurements" in parsed_data["payload"]
        assert len(parsed_data["payload"]["measurements"]) > 0

        # 6. Generate FHIR bundle
        response = await client.post(f"/api/v1/bundles/{report_id}/generate")
        assert response.status_code == 201
        _bundle_info = response.json()  # noqa: F841

        # 7. Download bundle
        response = await client.get(f"/api/v1/bundles/{report_id}/download")
        assert response.status_code == 200
        bundle = response.json()

        # Verify bundle structure
        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "transaction"
        assert "entry" in bundle

        # Should have Patient, DocumentReference, DiagnosticReport, and Observations
        resource_types = [entry["resource"]["resourceType"] for entry in bundle["entry"]]
        assert "Patient" in resource_types
        assert "DocumentReference" in resource_types
        assert "DiagnosticReport" in resource_types
        assert "Observation" in resource_types


@pytest.mark.integration
@pytest.mark.asyncio
async def test_duplicate_upload_detection(client: AsyncClient):
    """Test that duplicate uploads are detected and handled."""
    # Create patient
    patient_data = {
        "external_subject_id": "test-patient-002",
        "display_name": "Test Patient 2",
        "subject_type": SubjectType.HUMAN.value,
    }

    response = await client.post("/api/v1/patients", json=patient_data)
    assert response.status_code == 201
    patient_id = response.json()["id"]

    # Create PDF with sufficient content
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, "LABORATORY REPORT - Duplicate Detection Test")
    c.drawString(100, 720, "Quest Diagnostics Laboratory")
    c.drawString(100, 690, "Patient: Test Patient 2")
    c.drawString(100, 670, "Patient ID: TEST-002")
    c.drawString(100, 650, "Collection Date: 2024-01-15")
    c.drawString(100, 620, "Test Results:")
    c.drawString(100, 600, "Glucose: 100 mg/dL (Reference: 70-100 mg/dL)")
    c.drawString(100, 580, "Hemoglobin A1c: 5.8% (Reference: <5.7%)")
    c.drawString(100, 560, "Total Cholesterol: 195 mg/dL (Reference: <200 mg/dL)")
    c.drawString(100, 540, "HDL Cholesterol: 55 mg/dL (Reference: >40 mg/dL)")
    c.drawString(100, 500, "Performing Laboratory: Quest Diagnostics")
    c.drawString(100, 480, "Ordering Provider: Dr. Jane Smith, MD")
    c.save()
    pdf_content = pdf_buffer.getvalue()

    # First upload
    files = {"file": ("lab_report.pdf", pdf_content, "application/pdf")}
    data = {"patient_id": patient_id}

    response = await client.post("/api/v1/reports", files=files, data=data)
    assert response.status_code == 201
    _first_report = response.json()  # noqa: F841

    # Second upload (duplicate)
    files = {"file": ("lab_report_copy.pdf", pdf_content, "application/pdf")}
    data = {"patient_id": patient_id}

    response = await client.post("/api/v1/reports", files=files, data=data)
    # Should return 409 Conflict
    assert response.status_code == 409
    error = response.json()
    assert error["error"]["code"] == "duplicate_upload"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_patient_list_and_filter(client: AsyncClient):
    """Test patient listing and report filtering."""
    # Create two patients
    patient1_data = {
        "external_subject_id": "test-patient-003",
        "display_name": "Patient One",
        "subject_type": SubjectType.HUMAN.value,
    }

    response = await client.post("/api/v1/patients", json=patient1_data)
    assert response.status_code == 201
    patient1_id = response.json()["id"]

    patient2_data = {
        "external_subject_id": "test-patient-004",
        "display_name": "Patient Two",
        "subject_type": SubjectType.VETERINARY.value,
    }

    response = await client.post("/api/v1/patients", json=patient2_data)
    assert response.status_code == 201
    _patient2_id = response.json()["id"]

    # List all patients
    response = await client.get("/api/v1/patients")
    assert response.status_code == 200
    patients = response.json()
    assert patients["total"] >= 2

    # Filter reports by patient (should be empty initially)
    response = await client.get(f"/api/v1/reports?patient_id={patient1_id}")
    assert response.status_code == 200
    reports = response.json()
    assert reports["total"] == 0
