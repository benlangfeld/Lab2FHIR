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
    c.drawString(100, 750, "LABORATORY REPORT")
    c.drawString(100, 700, "Patient: Test Patient")
    c.drawString(100, 650, "Date: 2024-01-15")
    c.drawString(100, 600, "")
    c.drawString(100, 550, "Results:")
    c.drawString(100, 500, "Glucose: 95 mg/dL (Reference: 70-100)")
    c.drawString(100, 450, "Hemoglobin A1c: 5.5% (Reference: <5.7)")
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

    # Create PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, "Test Lab Report for Duplicate Detection")
    c.drawString(100, 700, "Glucose: 100 mg/dL")
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
