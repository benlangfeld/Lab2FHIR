"""Deterministic ID generation and normalization utilities."""

import hashlib
from datetime import datetime
from typing import Any


def generate_deterministic_id(
    *components: str | int | float | datetime | None, prefix: str = ""
) -> str:
    """
    Generate a deterministic identifier from components.

    Args:
        *components: Variable number of components to include in the ID
        prefix: Optional prefix for the generated ID

    Returns:
        Deterministic identifier as a string
    """
    # Normalize components to strings
    normalized_parts: list[str] = []

    for component in components:
        if component is None:
            normalized_parts.append("null")
        elif isinstance(component, datetime):
            # Use ISO format for datetime
            normalized_parts.append(component.isoformat())
        elif isinstance(component, (int, float)):
            normalized_parts.append(str(component))
        else:
            normalized_parts.append(str(component))

    # Join with pipe separator and hash
    composite_key = "|".join(normalized_parts)
    hash_value = hashlib.sha256(composite_key.encode("utf-8")).hexdigest()

    if prefix:
        return f"{prefix}-{hash_value[:16]}"
    return hash_value[:16]


def generate_observation_id(
    subject_id: str,
    collection_datetime: datetime,
    normalized_analyte: str,
    value: str | float | None,
    unit: str | None,
) -> str:
    """
    Generate deterministic Observation ID.

    The ID is based on:
    - Subject identifier
    - Collection datetime
    - Normalized analyte code
    - Value (numeric or string)
    - Unit (normalized)

    Args:
        subject_id: Patient/subject identifier
        collection_datetime: Sample collection datetime
        normalized_analyte: Canonical analyte code
        value: Measurement value (numeric or qualitative)
        unit: Normalized unit (UCUM if available)

    Returns:
        Deterministic observation identifier
    """
    return generate_deterministic_id(
        subject_id,
        collection_datetime,
        normalized_analyte,
        value,
        unit,
        prefix="obs",
    )


def generate_diagnostic_report_id(
    subject_id: str,
    report_datetime: datetime,
    file_hash: str,
) -> str:
    """
    Generate deterministic DiagnosticReport ID.

    Args:
        subject_id: Patient/subject identifier
        report_datetime: Report date/time
        file_hash: SHA-256 hash of the source file

    Returns:
        Deterministic diagnostic report identifier
    """
    return generate_deterministic_id(
        subject_id,
        report_datetime,
        file_hash[:16],  # Use first 16 chars of file hash
        prefix="diag",
    )


def generate_document_reference_id(file_hash: str) -> str:
    """
    Generate deterministic DocumentReference ID.

    Args:
        file_hash: SHA-256 hash of the source PDF

    Returns:
        Deterministic document reference identifier
    """
    return f"doc-{file_hash[:16]}"


def normalize_analyte_name(analyte_name: str) -> str:
    """
    Normalize analyte name for consistent comparison.

    Args:
        analyte_name: Original analyte name

    Returns:
        Normalized analyte name (uppercase, trimmed, spaces normalized)
    """
    # Convert to uppercase and strip whitespace
    normalized = analyte_name.upper().strip()

    # Normalize multiple spaces to single space
    normalized = " ".join(normalized.split())

    return normalized


def normalize_unit(unit: str) -> str:
    """
    Normalize unit string for consistent comparison.

    Args:
        unit: Original unit string

    Returns:
        Normalized unit string (lowercase, trimmed)
    """
    # Convert to lowercase and strip whitespace
    normalized = unit.lower().strip()

    # Common unit normalizations
    unit_mappings = {
        "mg/dl": "mg/dL",
        "g/dl": "g/dL",
        "mmol/l": "mmol/L",
        "micromol/l": "umol/L",
        "μmol/l": "umol/L",
        "ug/dl": "ug/dL",
        "μg/dl": "ug/dL",
        "ng/ml": "ng/mL",
        "pg/ml": "pg/mL",
        "iu/l": "IU/L",
        "u/l": "U/L",
        "cells/mm3": "cells/mm3",
        "cells/ul": "cells/uL",
        "cells/μl": "cells/uL",
        "%": "%",
        "percent": "%",
    }

    return unit_mappings.get(normalized, normalized)


def calculate_file_hash(content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content.

    Args:
        content: File content as bytes

    Returns:
        Hexadecimal SHA-256 hash string
    """
    return hashlib.sha256(content).hexdigest()


def hex_to_base64_bytes(hex_string: str) -> str:
    """
    Convert hexadecimal hash to base64-encoded bytes (for FHIR attachment hash).

    Args:
        hex_string: Hexadecimal string (e.g., from SHA-256)

    Returns:
        Base64-encoded string of the raw bytes
    """
    import base64

    # Convert hex string to bytes
    hash_bytes = bytes.fromhex(hex_string)

    # Encode to base64
    return base64.b64encode(hash_bytes).decode("ascii")
