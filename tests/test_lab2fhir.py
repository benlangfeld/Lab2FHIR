"""Tests for Lab2FHIR components."""

import pytest

from lab2fhir.normalizers import DateNormalizer, UnitNormalizer
from lab2fhir.schemas import LabReport, LabResult


class TestUnitNormalizer:
    """Tests for unit normalization."""

    def test_normalize_volume_units(self):
        normalizer = UnitNormalizer()
        assert normalizer.normalize("ml") == "mL"
        assert normalizer.normalize("ML") == "mL"
        assert normalizer.normalize("dl") == "dL"

    def test_normalize_mass_units(self):
        normalizer = UnitNormalizer()
        assert normalizer.normalize("gm") == "g"
        assert normalizer.normalize("mg") == "mg"
        assert normalizer.normalize("mcg") == "ug"

    def test_normalize_concentration_units(self):
        normalizer = UnitNormalizer()
        assert normalizer.normalize("mg/dl") == "mg/dL"
        assert normalizer.normalize("g/dl") == "g/dL"

    def test_normalize_none(self):
        normalizer = UnitNormalizer()
        assert normalizer.normalize(None) is None

    def test_normalize_unknown_unit(self):
        normalizer = UnitNormalizer()
        assert normalizer.normalize("xyz") == "xyz"


class TestDateNormalizer:
    """Tests for date normalization."""

    def test_normalize_iso_date(self):
        normalizer = DateNormalizer()
        assert normalizer.normalize("2024-01-15") == "2024-01-15"

    def test_normalize_us_date(self):
        normalizer = DateNormalizer()
        assert normalizer.normalize("01/15/2024") == "2024-01-15"

    def test_normalize_iso_datetime(self):
        normalizer = DateNormalizer()
        assert normalizer.normalize("2024-01-15T10:30:00") == "2024-01-15"

    def test_normalize_none(self):
        normalizer = DateNormalizer()
        assert normalizer.normalize(None) is None

    def test_normalize_invalid_date(self):
        normalizer = DateNormalizer()
        assert normalizer.normalize("invalid") is None

    def test_normalize_datetime_full(self):
        normalizer = DateNormalizer()
        result = normalizer.normalize_datetime("01/15/2024 10:30")
        assert result is not None
        assert "2024-01-15" in result

    def test_validate_valid_date(self):
        normalizer = DateNormalizer()
        is_valid, normalized = normalizer.validate("2024-01-15")
        assert is_valid
        assert normalized == "2024-01-15"

    def test_validate_invalid_date(self):
        normalizer = DateNormalizer()
        is_valid, normalized = normalizer.validate("invalid")
        assert not is_valid
        assert normalized is None


class TestSchemas:
    """Tests for Pydantic schemas."""

    def test_lab_result_creation(self):
        result = LabResult(
            test_name="Glucose",
            value="95",
            unit="mg/dL",
            reference_range="70-100 mg/dL",
        )
        assert result.test_name == "Glucose"
        assert result.value == "95"
        assert result.unit == "mg/dL"

    def test_lab_report_creation(self):
        results = [
            LabResult(
                test_name="Glucose",
                value="95",
                unit="mg/dL",
            )
        ]
        report = LabReport(
            patient_name="John Doe",
            patient_id="12345",
            results=results,
        )
        assert report.patient_name == "John Doe"
        assert report.patient_id == "12345"
        assert len(report.results) == 1

    def test_lab_report_json_export(self):
        results = [
            LabResult(
                test_name="Glucose",
                value="95",
                unit="mg/dL",
            )
        ]
        report = LabReport(results=results)
        json_str = report.model_dump_json()
        assert "Glucose" in json_str
        assert "95" in json_str
