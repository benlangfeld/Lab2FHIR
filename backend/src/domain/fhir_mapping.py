"""FHIR projection defaults and mapping helpers."""

from datetime import datetime
from typing import Any

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.identifier import Identifier
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference

from src.domain.intermediate_schema import LabMeasurement, ValueType


def create_identifier(system: str, value: str) -> Identifier:
    """
    Create a FHIR Identifier.

    Args:
        system: Identifier system URI
        value: Identifier value

    Returns:
        FHIR Identifier object
    """
    return Identifier(system=system, value=value)


def create_reference(resource_type: str, resource_id: str, display: str | None = None) -> Reference:
    """
    Create a FHIR Reference.

    Args:
        resource_type: Type of resource being referenced
        resource_id: ID of the resource
        display: Optional display text

    Returns:
        FHIR Reference object
    """
    ref = Reference(reference=f"{resource_type}/{resource_id}")
    if display:
        ref.display = display
    return ref


def create_coding(system: str, code: str, display: str | None = None) -> Coding:
    """
    Create a FHIR Coding.

    Args:
        system: Code system URI
        code: Code value
        display: Optional display text

    Returns:
        FHIR Coding object
    """
    coding = Coding(system=system, code=code)
    if display:
        coding.display = display
    return coding


def create_codeable_concept(
    system: str, code: str, display: str | None = None, text: str | None = None
) -> CodeableConcept:
    """
    Create a FHIR CodeableConcept.

    Args:
        system: Code system URI
        code: Code value
        display: Optional display text for the coding
        text: Optional text representation

    Returns:
        FHIR CodeableConcept object
    """
    coding = create_coding(system, code, display)
    concept = CodeableConcept(coding=[coding])
    if text:
        concept.text = text
    return concept


def create_quantity(
    value: float, unit: str, system: str = "http://unitsofmeasure.org", code: str | None = None
) -> Quantity:
    """
    Create a FHIR Quantity (typically with UCUM).

    Args:
        value: Numeric value
        unit: Unit display text
        system: Unit system URI (defaults to UCUM)
        code: Optional unit code (defaults to unit if not provided)

    Returns:
        FHIR Quantity object
    """
    return Quantity(value=value, unit=unit, system=system, code=code or unit)


def map_measurement_to_value(measurement: LabMeasurement) -> dict[str, Any]:
    """
    Map intermediate measurement to FHIR Observation value field.

    Args:
        measurement: Parsed lab measurement

    Returns:
        Dictionary with appropriate FHIR value field
    """
    if measurement.value_type == ValueType.NUMERIC:
        # Numeric value without operator
        unit = measurement.normalized_unit_ucum or measurement.original_unit or ""
        return {
            "valueQuantity": create_quantity(
                value=measurement.numeric_value,
                unit=unit,
                code=unit,
            ).dict(exclude_none=True)
        }

    elif measurement.value_type == ValueType.OPERATOR_NUMERIC:
        # Numeric value with comparison operator
        unit = measurement.normalized_unit_ucum or measurement.original_unit or ""
        operator_str = measurement.operator.value if measurement.operator else ""
        return {
            "valueQuantity": create_quantity(
                value=measurement.numeric_value,
                unit=unit,
                code=unit,
            ).dict(exclude_none=True),
            "interpretation": [
                CodeableConcept(text=f"{operator_str}{measurement.numeric_value} {unit}").dict(
                    exclude_none=True
                )
            ],
        }

    elif measurement.value_type == ValueType.QUALITATIVE:
        # Qualitative/text value
        return {"valueString": measurement.qualitative_value}

    else:
        raise ValueError(f"Unknown value type: {measurement.value_type}")


def format_datetime_for_fhir(dt: datetime) -> str:
    """
    Format datetime for FHIR (ISO 8601).

    Args:
        dt: Python datetime object

    Returns:
        ISO 8601 formatted string
    """
    return dt.isoformat()


def create_lab2fhir_extension(
    url: str, value_string: str | None = None, value_reference: Reference | None = None
) -> dict[str, Any]:
    """
    Create a custom Lab2FHIR extension.

    Args:
        url: Extension URL
        value_string: Optional string value
        value_reference: Optional reference value

    Returns:
        Extension dictionary
    """
    extension = {"url": url}
    if value_string is not None:
        extension["valueString"] = value_string
    if value_reference is not None:
        extension["valueReference"] = value_reference.dict(exclude_none=True)
    return extension


def get_loinc_code_for_analyte(normalized_analyte: str) -> tuple[str, str] | None:
    """
    Get LOINC code for common analytes.

    This is a minimal mapping for MVP. In production, this would be
    expanded or replaced with a comprehensive terminology service.

    Args:
        normalized_analyte: Normalized analyte code/name

    Returns:
        Tuple of (LOINC code, display) or None if not mapped
    """
    # Common analyte mappings
    loinc_map = {
        "GLU": ("2339-0", "Glucose [Mass/volume] in Blood"),
        "GLUCOSE": ("2339-0", "Glucose [Mass/volume] in Blood"),
        "HBA1C": ("4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood"),
        "HEMOGLOBIN A1C": ("4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood"),
        "CREATININE": ("2160-0", "Creatinine [Mass/volume] in Serum or Plasma"),
        "BUN": ("3094-0", "Urea nitrogen [Mass/volume] in Serum or Plasma"),
        "SODIUM": ("2951-2", "Sodium [Moles/volume] in Serum or Plasma"),
        "POTASSIUM": ("2823-3", "Potassium [Moles/volume] in Serum or Plasma"),
        "CHLORIDE": ("2075-0", "Chloride [Moles/volume] in Serum or Plasma"),
        "CO2": ("2028-9", "Carbon dioxide, total [Moles/volume] in Serum or Plasma"),
        "CALCIUM": ("17861-6", "Calcium [Mass/volume] in Serum or Plasma"),
        "ALT": (
            "1742-6",
            "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma",
        ),
        "AST": (
            "1920-8",
            "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma",
        ),
        "WBC": ("6690-2", "Leukocytes [#/volume] in Blood by Automated count"),
        "RBC": ("789-8", "Erythrocytes [#/volume] in Blood by Automated count"),
        "HEMOGLOBIN": ("718-7", "Hemoglobin [Mass/volume] in Blood"),
        "HEMATOCRIT": ("4544-3", "Hematocrit [Volume Fraction] of Blood by Automated count"),
        "PLATELETS": ("777-3", "Platelets [#/volume] in Blood by Automated count"),
    }

    normalized = normalized_analyte.upper().strip()
    return loinc_map.get(normalized)


# System URIs
SYSTEM_LAB2FHIR_SUBJECT_ID = "urn:lab2fhir:subject-id"
SYSTEM_LAB2FHIR_FILE_HASH = "urn:lab2fhir:file-sha256"
SYSTEM_LAB2FHIR_ANALYTE = "urn:lab2fhir:analyte"
SYSTEM_LOINC = "http://loinc.org"
SYSTEM_UCUM = "http://unitsofmeasure.org"
