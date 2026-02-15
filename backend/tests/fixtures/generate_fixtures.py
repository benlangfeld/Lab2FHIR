"""Script to generate synthetic fixture PDFs for testing."""

import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    print("reportlab not installed. Install with: pip install reportlab")
    exit(1)


def create_basic_lab_pdf():
    """Create a basic lab report PDF with numeric values."""
    output_path = Path(__file__).parent / "us1" / "lab_numeric_basic.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "LABORATORY REPORT")

    # Patient info
    c.setFont("Helvetica", 12)
    y_pos = height - 100
    c.drawString(50, y_pos, "Patient: John Doe")
    y_pos -= 20
    c.drawString(50, y_pos, "Patient ID: TEST-001")
    y_pos -= 20
    c.drawString(50, y_pos, f"Report Date: {datetime.now().strftime('%Y-%m-%d')}")
    y_pos -= 20
    c.drawString(50, y_pos, "Specimen Collection: 2024-01-15 08:00:00")

    # Results section
    y_pos -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "Test Results")

    c.setFont("Helvetica", 11)
    y_pos -= 30

    # Table header
    c.drawString(50, y_pos, "Test Name")
    c.drawString(250, y_pos, "Value")
    c.drawString(350, y_pos, "Unit")
    c.drawString(450, y_pos, "Reference Range")

    y_pos -= 5
    c.line(50, y_pos, width - 50, y_pos)
    y_pos -= 20

    # Glucose
    c.drawString(50, y_pos, "Glucose")
    c.drawString(250, y_pos, "95.0")
    c.drawString(350, y_pos, "mg/dL")
    c.drawString(450, y_pos, "70-100 mg/dL")
    y_pos -= 20

    # Hemoglobin A1c
    c.drawString(50, y_pos, "Hemoglobin A1c")
    c.drawString(250, y_pos, "5.5")
    c.drawString(350, y_pos, "%")
    c.drawString(450, y_pos, "<5.7%")
    y_pos -= 20

    # Creatinine
    c.drawString(50, y_pos, "Creatinine")
    c.drawString(250, y_pos, "1.0")
    c.drawString(350, y_pos, "mg/dL")
    c.drawString(450, y_pos, "0.7-1.3 mg/dL")
    y_pos -= 20

    # Footer
    y_pos -= 40
    c.setFont("Helvetica-Italic", 10)
    c.drawString(50, y_pos, "Performing Laboratory: Quest Diagnostics")
    y_pos -= 15
    c.drawString(50, y_pos, "Ordering Provider: Dr. Jane Smith")

    c.save()
    print(f"Created: {output_path}")

    # Create expected parsed JSON
    expected_parsed = {
        "schema_version": "1.0",
        "subject_identifier": "TEST-001",
        "report_date": "2024-01-15T08:00:00Z",
        "ordering_provider": "Dr. Jane Smith",
        "performing_lab": "Quest Diagnostics",
        "measurements": [
            {
                "original_analyte_name": "Glucose",
                "normalized_analyte_code": "GLU",
                "value_type": "numeric",
                "numeric_value": 95.0,
                "operator": None,
                "qualitative_value": None,
                "original_unit": "mg/dL",
                "normalized_unit_ucum": "mg/dL",
                "reference_range_text": "70-100 mg/dL",
                "collection_datetime": "2024-01-15T08:00:00Z",
                "result_datetime": None,
            },
            {
                "original_analyte_name": "Hemoglobin A1c",
                "normalized_analyte_code": "HBA1C",
                "value_type": "numeric",
                "numeric_value": 5.5,
                "operator": None,
                "qualitative_value": None,
                "original_unit": "%",
                "normalized_unit_ucum": "%",
                "reference_range_text": "<5.7%",
                "collection_datetime": "2024-01-15T08:00:00Z",
                "result_datetime": None,
            },
            {
                "original_analyte_name": "Creatinine",
                "normalized_analyte_code": "CREATININE",
                "value_type": "numeric",
                "numeric_value": 1.0,
                "operator": None,
                "qualitative_value": None,
                "original_unit": "mg/dL",
                "normalized_unit_ucum": "mg/dL",
                "reference_range_text": "0.7-1.3 mg/dL",
                "collection_datetime": "2024-01-15T08:00:00Z",
                "result_datetime": None,
            },
        ],
    }

    expected_path = Path(__file__).parent / "us1" / "lab_numeric_basic_expected.json"
    with open(expected_path, "w") as f:
        json.dump(expected_parsed, f, indent=2)
    print(f"Created: {expected_path}")


if __name__ == "__main__":
    create_basic_lab_pdf()
    print("\n✅ Fixture PDFs generated successfully!")
