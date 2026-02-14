"""Main pipeline orchestrating the Lab2FHIR workflow."""

from pathlib import Path
from typing import Optional

from .fhir_client import FHIRClient
from .fhir_converter import FHIRConverter
from .parser import LabReportParser
from .pdf_extractor import PDFExtractor
from .schemas import LabReport


class Lab2FHIRPipeline:
    """Main pipeline for converting lab PDFs to FHIR resources."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        fhir_server_url: Optional[str] = None,
        fhir_auth_token: Optional[str] = None,
    ):
        """
        Initialize the pipeline.

        Args:
            openai_api_key: OpenAI API key (defaults to env var)
            fhir_server_url: FHIR server URL (defaults to env var)
            fhir_auth_token: FHIR server auth token (defaults to env var)
        """
        self.pdf_extractor = PDFExtractor()
        self.parser = LabReportParser(api_key=openai_api_key)
        self.fhir_converter = FHIRConverter()
        self.fhir_client = FHIRClient(
            server_url=fhir_server_url, auth_token=fhir_auth_token
        )

    def process_pdf(
        self,
        pdf_path: str,
        output_json_path: Optional[str] = None,
        output_fhir_path: Optional[str] = None,
        post_to_server: bool = True,
    ) -> dict:
        """
        Process a lab report PDF through the complete pipeline.

        Args:
            pdf_path: Path to the PDF file
            output_json_path: Optional path to save intermediate JSON
            output_fhir_path: Optional path to save FHIR bundle JSON
            post_to_server: Whether to POST to FHIR server

        Returns:
            Dictionary with processing results and server response

        Raises:
            Exception: If any step fails
        """
        pdf_file = Path(pdf_path)
        pdf_filename = pdf_file.name

        # Step 1: Extract text and base64 from PDF
        print(f"Extracting text from {pdf_filename}...")
        text, pdf_base64 = self.pdf_extractor.extract_all(pdf_path)

        # Step 2: Parse with OpenAI
        print("Parsing lab report with OpenAI...")
        lab_report = self.parser.parse(text)

        # Save intermediate JSON if requested
        if output_json_path:
            print(f"Saving intermediate JSON to {output_json_path}...")
            with open(output_json_path, "w") as f:
                f.write(lab_report.model_dump_json(indent=2))

        # Step 3: Convert to FHIR Bundle
        print("Converting to FHIR R4 Bundle...")
        fhir_bundle = self.fhir_converter.convert_to_bundle(
            lab_report, pdf_base64, pdf_filename
        )

        # Save FHIR bundle if requested
        if output_fhir_path:
            print(f"Saving FHIR bundle to {output_fhir_path}...")
            with open(output_fhir_path, "w") as f:
                f.write(self.fhir_converter.bundle_to_json(fhir_bundle))

        # Step 4: POST to FHIR server
        server_response = None
        if post_to_server:
            print(f"Posting to FHIR server at {self.fhir_client.server_url}...")
            try:
                server_response = self.fhir_client.post_bundle(fhir_bundle)
                print("Successfully posted to FHIR server!")
            except Exception as e:
                print(f"Warning: Failed to post to FHIR server: {e}")
                server_response = {"error": str(e)}

        return {
            "pdf_file": pdf_filename,
            "lab_report": lab_report.model_dump(),
            "fhir_bundle_id": fhir_bundle.id,
            "resource_count": len(fhir_bundle.entry) if fhir_bundle.entry else 0,
            "server_response": server_response,
        }

    def process_text(
        self,
        text: str,
        pdf_base64: Optional[str] = None,
        output_json_path: Optional[str] = None,
        output_fhir_path: Optional[str] = None,
        post_to_server: bool = True,
    ) -> dict:
        """
        Process lab report text (without PDF file).

        Args:
            text: Lab report text
            pdf_base64: Optional base64 encoded PDF
            output_json_path: Optional path to save intermediate JSON
            output_fhir_path: Optional path to save FHIR bundle JSON
            post_to_server: Whether to POST to FHIR server

        Returns:
            Dictionary with processing results
        """
        # Parse with OpenAI
        print("Parsing lab report with OpenAI...")
        lab_report = self.parser.parse(text)

        # Save intermediate JSON if requested
        if output_json_path:
            print(f"Saving intermediate JSON to {output_json_path}...")
            with open(output_json_path, "w") as f:
                f.write(lab_report.model_dump_json(indent=2))

        # Convert to FHIR Bundle
        print("Converting to FHIR R4 Bundle...")
        pdf_data = pdf_base64 or ""  # Use empty string if no PDF provided
        fhir_bundle = self.fhir_converter.convert_to_bundle(
            lab_report, pdf_data, "lab_report.pdf"
        )

        # Save FHIR bundle if requested
        if output_fhir_path:
            print(f"Saving FHIR bundle to {output_fhir_path}...")
            with open(output_fhir_path, "w") as f:
                f.write(self.fhir_converter.bundle_to_json(fhir_bundle))

        # POST to FHIR server
        server_response = None
        if post_to_server:
            print(f"Posting to FHIR server at {self.fhir_client.server_url}...")
            try:
                server_response = self.fhir_client.post_bundle(fhir_bundle)
                print("Successfully posted to FHIR server!")
            except Exception as e:
                print(f"Warning: Failed to post to FHIR server: {e}")
                server_response = {"error": str(e)}

        return {
            "lab_report": lab_report.model_dump(),
            "fhir_bundle_id": fhir_bundle.id,
            "resource_count": len(fhir_bundle.entry) if fhir_bundle.entry else 0,
            "server_response": server_response,
        }
