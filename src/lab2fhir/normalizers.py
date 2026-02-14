"""Unit and date validation/normalization utilities."""

import re
from datetime import datetime
from typing import Optional, Tuple


class UnitNormalizer:
    """Normalize lab test units to standard formats."""

    # Common unit mappings to standard UCUM units
    UNIT_MAPPINGS = {
        # Volume
        "ml": "mL",
        "ML": "mL",
        "dl": "dL",
        "DL": "dL",
        "l": "L",
        # Mass
        "gm": "g",
        "GM": "g",
        "mg": "mg",
        "MG": "mg",
        "ug": "ug",
        "UG": "ug",
        "mcg": "ug",
        "MCG": "ug",
        # Concentration
        "mg/dl": "mg/dL",
        "g/dl": "g/dL",
        "mmol/l": "mmol/L",
        "umol/l": "umol/L",
        # Count
        "cells/ul": "10*3/uL",
        "k/ul": "10*3/uL",
        "/ul": "/uL",
        # Percentage
        "percent": "%",
        # Time
        "sec": "s",
        "min": "min",
        "hr": "h",
        "hour": "h",
    }

    def normalize(self, unit: Optional[str]) -> Optional[str]:
        """
        Normalize a unit string to standard format.

        Args:
            unit: Original unit string

        Returns:
            Normalized unit string or None if input is None
        """
        if not unit:
            return None

        # Trim whitespace
        unit = unit.strip()

        # Check for exact mapping
        if unit in self.UNIT_MAPPINGS:
            return self.UNIT_MAPPINGS[unit]

        # Case-insensitive lookup
        unit_lower = unit.lower()
        for key, value in self.UNIT_MAPPINGS.items():
            if key.lower() == unit_lower:
                return value

        # Return original if no mapping found
        return unit


class DateNormalizer:
    """Normalize and validate date strings."""

    # Common date formats to try
    DATE_FORMATS = [
        "%Y-%m-%d",  # ISO format
        "%Y-%m-%dT%H:%M:%S",  # ISO datetime
        "%Y-%m-%dT%H:%M:%S.%f",  # ISO datetime with microseconds
        "%m/%d/%Y",  # US format
        "%m-%d-%Y",  # US format with dashes
        "%d/%m/%Y",  # European format
        "%d-%m-%Y",  # European format with dashes
        "%B %d, %Y",  # January 01, 2024
        "%b %d, %Y",  # Jan 01, 2024
        "%m/%d/%Y %H:%M",  # US datetime
        "%m/%d/%Y %H:%M:%S",  # US datetime with seconds
    ]

    def normalize(self, date_str: Optional[str]) -> Optional[str]:
        """
        Normalize a date string to ISO 8601 format (YYYY-MM-DD).

        Args:
            date_str: Original date string

        Returns:
            ISO 8601 formatted date string or None if invalid/None
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Try each format
        for fmt in self.DATE_FORMATS:
            try:
                dt = datetime.strptime(date_str, fmt)
                # Return date only (YYYY-MM-DD)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # Try to parse ISO format with timezone
        try:
            # Remove timezone info if present and parse
            # First remove Z suffix, then remove timezone offset
            date_str_clean = date_str
            if date_str_clean.endswith('Z'):
                date_str_clean = date_str_clean[:-1]
            else:
                # Remove timezone offset like +00:00 or -05:00
                date_str_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str_clean)
            
            dt = datetime.fromisoformat(date_str_clean)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            pass

        # Return None if no format matches
        return None

    def normalize_datetime(self, datetime_str: Optional[str]) -> Optional[str]:
        """
        Normalize a datetime string to ISO 8601 format with time.

        Args:
            datetime_str: Original datetime string

        Returns:
            ISO 8601 formatted datetime string or None if invalid/None
        """
        if not datetime_str:
            return None

        datetime_str = datetime_str.strip()

        # Try each format
        for fmt in self.DATE_FORMATS:
            try:
                dt = datetime.strptime(datetime_str, fmt)
                # Return full datetime in ISO format
                return dt.isoformat()
            except ValueError:
                continue

        # Try to parse ISO format
        try:
            # Remove timezone info if present and parse
            datetime_str_clean = datetime_str
            if datetime_str_clean.endswith('Z'):
                datetime_str_clean = datetime_str_clean[:-1]
            else:
                # Remove timezone offset like +00:00 or -05:00
                datetime_str_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', datetime_str_clean)
            
            dt = datetime.fromisoformat(datetime_str_clean)
            return dt.isoformat()
        except (ValueError, AttributeError):
            pass

        return None

    def validate(self, date_str: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate and normalize a date string.

        Args:
            date_str: Date string to validate

        Returns:
            Tuple of (is_valid, normalized_date)
        """
        if not date_str:
            return True, None  # None is valid

        normalized = self.normalize(date_str)
        return normalized is not None, normalized
