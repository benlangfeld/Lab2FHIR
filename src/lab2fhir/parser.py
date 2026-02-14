"""OpenAI-based parser using structured outputs."""

import json
import os
from typing import Optional

from openai import OpenAI
from pydantic import ValidationError

from .schemas import LabReport


class LabReportParser:
    """Parse lab report text using OpenAI Structured Outputs."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-2024-08-06"):
        """
        Initialize the parser.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (must support structured outputs)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def parse(self, text: str) -> LabReport:
        """
        Parse lab report text into structured format.

        Args:
            text: Raw text extracted from lab report PDF

        Returns:
            Structured LabReport object

        Raises:
            Exception: If parsing fails
        """
        system_prompt = """You are a medical lab report parser. Extract structured information from lab reports.
        
Guidelines:
- Extract all patient demographics accurately
- Parse all lab test results with their values and units
- Identify abnormal flags (H for High, L for Low, A for Abnormal)
- Extract reference ranges when available
- Parse dates in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- If information is not present in the report, leave the field as null
- Be precise with numerical values and units"""

        try:
            # Using the structured output feature with response_format
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Parse this lab report:\n\n{text}",
                    },
                ],
                response_format=LabReport,
            )

            # Extract the parsed response
            parsed_report = completion.choices[0].message.parsed

            if parsed_report is None:
                raise Exception("Failed to parse lab report: No structured output returned")

            return parsed_report

        except ValidationError as e:
            raise Exception(f"Validation error in parsed report: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to parse lab report with OpenAI: {e}") from e

    def parse_to_json(self, text: str) -> str:
        """
        Parse lab report text and return as JSON string.

        Args:
            text: Raw text extracted from lab report PDF

        Returns:
            JSON string of structured lab report

        Raises:
            Exception: If parsing fails
        """
        report = self.parse(text)
        return report.model_dump_json(indent=2)
