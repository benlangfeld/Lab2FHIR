"""Intermediate schema models for parsed lab data."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ValueType(str, Enum):
    """Type of measurement value."""

    NUMERIC = "numeric"
    QUALITATIVE = "qualitative"
    OPERATOR_NUMERIC = "operator_numeric"


class ComparisonOperator(str, Enum):
    """Comparison operator for numeric values."""

    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="


class LabMeasurement(BaseModel):
    """Individual lab measurement within a report."""

    # Analyte identification
    original_analyte_name: str = Field(
        ..., min_length=1, max_length=500, description="Original analyte name from PDF"
    )
    normalized_analyte_code: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Canonical analyte code after normalization",
    )

    # Value representation
    value_type: ValueType = Field(..., description="Type of value stored")
    numeric_value: float | None = Field(None, description="Numeric value if applicable")
    operator: ComparisonOperator | None = Field(None, description="Comparison operator if applicable")
    qualitative_value: str | None = Field(
        None, max_length=500, description="Qualitative value if applicable"
    )

    # Units
    original_unit: str | None = Field(None, max_length=100, description="Original unit from PDF")
    normalized_unit_ucum: str | None = Field(
        None, max_length=100, description="UCUM-normalized unit"
    )

    # Reference range
    reference_range_text: str | None = Field(
        None, max_length=500, description="Reference range as text"
    )

    # Timing
    collection_datetime: datetime = Field(
        ..., description="Sample collection date/time (ISO 8601)"
    )
    result_datetime: datetime | None = Field(
        None, description="Result/test date/time if different from collection"
    )

    @field_validator("numeric_value")
    @classmethod
    def validate_numeric_value(cls, v: float | None, info) -> float | None:
        """Validate that numeric_value is present when required."""
        value_type = info.data.get("value_type")
        if value_type in (ValueType.NUMERIC, ValueType.OPERATOR_NUMERIC) and v is None:
            raise ValueError("numeric_value is required for numeric and operator_numeric types")
        return v

    @field_validator("qualitative_value")
    @classmethod
    def validate_qualitative_value(cls, v: str | None, info) -> str | None:
        """Validate that qualitative_value is present when required."""
        value_type = info.data.get("value_type")
        if value_type == ValueType.QUALITATIVE and not v:
            raise ValueError("qualitative_value is required for qualitative type")
        return v

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: ComparisonOperator | None, info) -> ComparisonOperator | None:
        """Validate that operator is present when required."""
        value_type = info.data.get("value_type")
        if value_type == ValueType.OPERATOR_NUMERIC and v is None:
            raise ValueError("operator is required for operator_numeric type")
        return v

    @field_validator("collection_datetime")
    @classmethod
    def validate_collection_not_future(cls, v: datetime) -> datetime:
        """Validate that collection datetime is not in the future."""
        if v > datetime.now(v.tzinfo):
            raise ValueError("collection_datetime cannot be in the future")
        return v


class ParsedLabData(BaseModel):
    """Complete parsed lab data from a single PDF report."""

    schema_version: str = Field(
        default="1.0", description="Version of this intermediate schema"
    )

    # Patient/subject information
    subject_identifier: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Subject identifier extracted from report (if present)",
    )

    # Report metadata
    report_date: datetime | None = Field(
        None, description="Overall report date/time if present"
    )
    ordering_provider: str | None = Field(
        None, max_length=500, description="Ordering provider name if present"
    )
    performing_lab: str | None = Field(
        None, max_length=500, description="Performing laboratory name if present"
    )

    # Measurements
    measurements: list[LabMeasurement] = Field(
        ..., min_length=1, description="List of lab measurements extracted from the report"
    )

    @field_validator("measurements")
    @classmethod
    def validate_measurements_not_empty(cls, v: list[LabMeasurement]) -> list[LabMeasurement]:
        """Validate that at least one measurement is present."""
        if not v:
            raise ValueError("At least one measurement is required")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "schema_version": "1.0",
                "subject_identifier": "patient-12345",
                "report_date": "2024-01-15T10:30:00Z",
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
                        "result_datetime": "2024-01-15T10:30:00Z",
                    }
                ],
            }
        }
