"""PDF text extraction service with scanned-PDF detection."""

from typing import BinaryIO

import pdfplumber

from src.api.errors import ParsingError, ScannedPDFError


class PDFExtractionService:
    """Service for extracting text from PDF files."""

    @staticmethod
    def extract_text(pdf_content: bytes) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            Extracted text

        Raises:
            ScannedPDFError: If PDF appears to be scanned/image-based
            ParsingError: If PDF extraction fails
        """
        try:
            # Use pdfplumber to extract text
            import io

            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                # Extract text from all pages
                text_pages = []
                total_chars = 0

                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_pages.append(page_text)
                        total_chars += len(page_text.strip())

                # Check if we have meaningful text content
                if total_chars < 50:  # Threshold for minimum text content
                    raise ScannedPDFError()

                # Join all pages with double newline
                full_text = "\n\n".join(text_pages)

                # Additional heuristic: Check for common lab report indicators
                # If we have very little text, it's likely scanned
                words = full_text.split()
                if len(words) < 20:
                    raise ScannedPDFError()

                return full_text

        except ScannedPDFError:
            raise
        except Exception as e:
            raise ParsingError(
                f"Failed to extract text from PDF: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    @staticmethod
    def is_text_based_pdf(pdf_content: bytes) -> bool:
        """
        Check if PDF is text-based (not scanned).

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            True if text-based, False if scanned/image-based
        """
        try:
            text = PDFExtractionService.extract_text(pdf_content)
            return len(text.strip()) >= 50
        except ScannedPDFError:
            return False
        except Exception:
            return False


def get_pdf_extraction_service() -> PDFExtractionService:
    """Get PDF extraction service instance."""
    return PDFExtractionService()
