"""PDF text extraction module."""

import base64
from pathlib import Path
from typing import Tuple

from pypdf import PdfReader


class PDFExtractor:
    """Extract text and base64 content from PDF files."""

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: If PDF reading fails
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            reader = PdfReader(pdf_path)
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n\n".join(text_parts)
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}") from e

    def encode_pdf_base64(self, pdf_path: str) -> str:
        """
        Encode PDF file as base64 string.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Base64 encoded string of the PDF

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            return base64.b64encode(pdf_bytes).decode("utf-8")

    def extract_all(self, pdf_path: str) -> Tuple[str, str]:
        """
        Extract both text and base64 encoded content from PDF.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (text_content, base64_encoded_pdf)
        """
        text = self.extract_text(pdf_path)
        base64_pdf = self.encode_pdf_base64(pdf_path)
        return text, base64_pdf
