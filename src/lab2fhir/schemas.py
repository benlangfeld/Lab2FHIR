"""Intermediate JSON schema for parsed lab results."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class LabResult(BaseModel):
    """Individual lab test result."""

    test_name: str = Field(description="Name of the lab test")
    value: str = Field(description="The test result value")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    reference_range: Optional[str] = Field(
        default=None, description="Normal reference range for this test"
    )
    abnormal_flag: Optional[str] = Field(
        default=None, description="Flag indicating abnormal result (e.g., H, L, A)"
    )


class LabReport(BaseModel):
    """Complete lab report with all results."""

    patient_name: Optional[str] = Field(default=None, description="Patient's full name")
    patient_id: Optional[str] = Field(
        default=None, description="Patient identifier (MRN, etc.)"
    )
    date_of_birth: Optional[str] = Field(
        default=None, description="Patient's date of birth (YYYY-MM-DD)"
    )
    collection_date: Optional[str] = Field(
        default=None, description="Specimen collection date/time (ISO 8601 format)"
    )
    report_date: Optional[str] = Field(
        default=None, description="Report issued date/time (ISO 8601 format)"
    )
    ordering_provider: Optional[str] = Field(
        default=None, description="Name of ordering physician"
    )
    lab_name: Optional[str] = Field(
        default=None, description="Name of the laboratory"
    )
    specimen_type: Optional[str] = Field(
        default=None, description="Type of specimen (e.g., Blood, Urine)"
    )
    results: List[LabResult] = Field(
        default_factory=list, description="List of lab test results"
    )
    notes: Optional[str] = Field(
        default=None, description="Additional notes or comments"
    )
