"""Unit tests for foundational components: schema validation, state machine, determinism."""

from datetime import datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.domain.determinism import (
    calculate_file_hash,
    generate_diagnostic_report_id,
    generate_document_reference_id,
    generate_observation_id,
    hex_to_base64_bytes,
    normalize_analyte_name,
    normalize_unit,
)
from src.domain.intermediate_schema import (
    ComparisonOperator,
    LabMeasurement,
    ParsedLabData,
    ValueType,
)
from src.domain.report_state_machine import (
    StateTransitionError,
    can_transition,
    get_allowed_transitions,
    get_status_metadata,
    is_terminal_status,
    validate_transition,
)
from src.db.models import ReportStatus


class TestIntermediateSchema:
    """Tests for intermediate schema validation."""

    def test_valid_numeric_measurement(self):
        """Test creating a valid numeric measurement."""
        measurement = LabMeasurement(
            original_analyte_name="Glucose",
            value_type=ValueType.NUMERIC,
            numeric_value=95.0,
            original_unit="mg/dL",
            collection_datetime=datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC),
        )
        assert measurement.numeric_value == 95.0
        assert measurement.value_type == ValueType.NUMERIC

    def test_valid_operator_numeric_measurement(self):
        """Test creating a valid operator-numeric measurement."""
        measurement = LabMeasurement(
            original_analyte_name="PSA",
            value_type=ValueType.OPERATOR_NUMERIC,
            numeric_value=0.1,
            operator=ComparisonOperator.LESS_THAN,
            original_unit="ng/mL",
            collection_datetime=datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC),
        )
        assert measurement.operator == ComparisonOperator.LESS_THAN
        assert measurement.numeric_value == 0.1

    def test_valid_qualitative_measurement(self):
        """Test creating a valid qualitative measurement."""
        measurement = LabMeasurement(
            original_analyte_name="Blood Type",
            value_type=ValueType.QUALITATIVE,
            qualitative_value="O Positive",
            collection_datetime=datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC),
        )
        assert measurement.qualitative_value == "O Positive"

    def test_numeric_requires_value(self):
        """Test that numeric type requires numeric_value."""
        with pytest.raises(PydanticValidationError) as exc_info:
            LabMeasurement(
                original_analyte_name="Glucose",
                value_type=ValueType.NUMERIC,
                collection_datetime=datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC),
            )
        assert "numeric_value is required" in str(exc_info.value)

    def test_qualitative_requires_value(self):
        """Test that qualitative type requires qualitative_value."""
        with pytest.raises(PydanticValidationError) as exc_info:
            LabMeasurement(
                original_analyte_name="Blood Type",
                value_type=ValueType.QUALITATIVE,
                collection_datetime=datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC),
            )
        assert "qualitative_value is required" in str(exc_info.value)

    def test_operator_numeric_requires_operator(self):
        """Test that operator_numeric type requires operator."""
        with pytest.raises(PydanticValidationError) as exc_info:
            LabMeasurement(
                original_analyte_name="PSA",
                value_type=ValueType.OPERATOR_NUMERIC,
                numeric_value=0.1,
                collection_datetime=datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC),
            )
        assert "operator is required" in str(exc_info.value)

    def test_parsed_lab_data_valid(self):
        """Test creating valid parsed lab data."""
        measurement = LabMeasurement(
            original_analyte_name="Glucose",
            value_type=ValueType.NUMERIC,
            numeric_value=95.0,
            original_unit="mg/dL",
            collection_datetime=datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC),
        )
        parsed_data = ParsedLabData(
            schema_version="1.0",
            measurements=[measurement],
        )
        assert len(parsed_data.measurements) == 1
        assert parsed_data.schema_version == "1.0"

    def test_parsed_lab_data_requires_measurements(self):
        """Test that parsed lab data requires at least one measurement."""
        with pytest.raises(PydanticValidationError) as exc_info:
            ParsedLabData(schema_version="1.0", measurements=[])
        assert "At least one measurement is required" in str(exc_info.value)


class TestReportStateMachine:
    """Tests for report state machine."""

    def test_valid_transition_uploaded_to_parsing(self):
        """Test valid transition from uploaded to parsing."""
        assert can_transition(ReportStatus.UPLOADED, ReportStatus.PARSING)
        validate_transition(ReportStatus.UPLOADED, ReportStatus.PARSING)  # Should not raise

    def test_valid_transition_parsing_to_review_pending(self):
        """Test valid transition from parsing to review_pending."""
        assert can_transition(ReportStatus.PARSING, ReportStatus.REVIEW_PENDING)

    def test_invalid_transition_uploaded_to_completed(self):
        """Test invalid transition from uploaded to completed."""
        assert not can_transition(ReportStatus.UPLOADED, ReportStatus.COMPLETED)
        with pytest.raises(StateTransitionError):
            validate_transition(ReportStatus.UPLOADED, ReportStatus.COMPLETED)

    def test_duplicate_is_terminal(self):
        """Test that duplicate status is terminal."""
        assert is_terminal_status(ReportStatus.DUPLICATE)
        assert len(get_allowed_transitions(ReportStatus.DUPLICATE)) == 0

    def test_completed_can_transition_to_editing(self):
        """Test that completed reports can be edited."""
        assert can_transition(ReportStatus.COMPLETED, ReportStatus.EDITING)

    def test_status_metadata(self):
        """Test status metadata retrieval."""
        metadata = get_status_metadata(ReportStatus.PARSING)
        assert metadata["status"] == "parsing"
        assert metadata["is_processing"] is True
        assert metadata["is_user_actionable"] is False


class TestDeterminism:
    """Tests for deterministic ID generation and normalization."""

    def test_observation_id_deterministic(self):
        """Test that observation ID generation is deterministic."""
        dt = datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC)
        id1 = generate_observation_id("patient-123", dt, "GLU", 95.0, "mg/dL")
        id2 = generate_observation_id("patient-123", dt, "GLU", 95.0, "mg/dL")
        assert id1 == id2
        assert id1.startswith("obs-")

    def test_observation_id_different_values(self):
        """Test that different values produce different IDs."""
        dt = datetime(2024, 1, 15, 8, 0, 0, tzinfo=datetime.UTC)
        id1 = generate_observation_id("patient-123", dt, "GLU", 95.0, "mg/dL")
        id2 = generate_observation_id("patient-123", dt, "GLU", 100.0, "mg/dL")
        assert id1 != id2

    def test_diagnostic_report_id_deterministic(self):
        """Test that diagnostic report ID generation is deterministic."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=datetime.UTC)
        file_hash = "abc123def456"
        id1 = generate_diagnostic_report_id("patient-123", dt, file_hash)
        id2 = generate_diagnostic_report_id("patient-123", dt, file_hash)
        assert id1 == id2
        assert id1.startswith("diag-")

    def test_document_reference_id_deterministic(self):
        """Test that document reference ID generation is deterministic."""
        file_hash = "abc123def456"
        id1 = generate_document_reference_id(file_hash)
        id2 = generate_document_reference_id(file_hash)
        assert id1 == id2
        assert id1.startswith("doc-")

    def test_normalize_analyte_name(self):
        """Test analyte name normalization."""
        assert normalize_analyte_name("  glucose  ") == "GLUCOSE"
        assert normalize_analyte_name("Hemoglobin A1c") == "HEMOGLOBIN A1C"
        assert normalize_analyte_name("  Multi   Space   ") == "MULTI SPACE"

    def test_normalize_unit(self):
        """Test unit normalization."""
        assert normalize_unit("mg/dl") == "mg/dL"
        assert normalize_unit("MG/DL") == "mg/dL"
        assert normalize_unit("mmol/l") == "mmol/L"
        assert normalize_unit("μmol/L") == "umol/L"

    def test_file_hash_calculation(self):
        """Test file hash calculation."""
        content = b"test content"
        hash1 = calculate_file_hash(content)
        hash2 = calculate_file_hash(content)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters

    def test_hex_to_base64_conversion(self):
        """Test hex to base64 conversion for FHIR hash."""
        hex_hash = "abc123def456"
        base64_hash = hex_to_base64_bytes(hex_hash)
        assert isinstance(base64_hash, str)
        # Should be base64 encoded
        import base64

        # Verify it can be decoded back
        decoded = base64.b64decode(base64_hash)
        assert decoded == bytes.fromhex(hex_hash)
