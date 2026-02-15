"""Storage service abstraction for PDFs and FHIR bundles."""

import json
import uuid
from pathlib import Path

from src.config import get_settings


class StorageService:
    """Service for storing and retrieving files (PDFs, bundles)."""

    def __init__(self):
        """Initialize storage service with configured paths."""
        self.settings = get_settings()
        self.pdf_storage_path = Path(self.settings.pdf_storage_path)
        self.bundle_storage_path = Path(self.settings.bundle_storage_path)

        # Ensure storage directories exist
        self.pdf_storage_path.mkdir(parents=True, exist_ok=True)
        self.bundle_storage_path.mkdir(parents=True, exist_ok=True)

    def store_pdf(self, content: bytes, original_filename: str, file_hash: str) -> str:
        """
        Store a PDF file.

        Args:
            content: PDF file content as bytes
            original_filename: Original filename for reference
            file_hash: SHA-256 hash of the file content

        Returns:
            Storage URI for the stored file
        """
        # Use hash-based filename to avoid duplicates and name collisions
        filename = f"{file_hash}.pdf"
        file_path = self.pdf_storage_path / filename

        # Write file if it doesn't already exist (deduplication)
        if not file_path.exists():
            file_path.write_bytes(content)

        # Return relative path as URI
        return f"file://{file_path.absolute()}"

    def retrieve_pdf(self, storage_uri: str) -> bytes:
        """
        Retrieve a PDF file from storage.

        Args:
            storage_uri: Storage URI returned by store_pdf

        Returns:
            PDF file content as bytes

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        # Extract path from URI
        if storage_uri.startswith("file://"):
            file_path = Path(storage_uri.replace("file://", ""))
        else:
            file_path = self.pdf_storage_path / storage_uri

        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found at {storage_uri}")

        return file_path.read_bytes()

    def store_bundle(self, bundle_data: dict, report_id: uuid.UUID, bundle_hash: str) -> str:
        """
        Store a FHIR bundle as JSON.

        Args:
            bundle_data: FHIR bundle as dictionary
            report_id: ID of the associated report
            bundle_hash: SHA-256 hash of the bundle content

        Returns:
            Storage URI for the stored bundle
        """
        # Use report ID and hash for filename
        filename = f"{report_id}_{bundle_hash[:16]}.json"
        file_path = self.bundle_storage_path / filename

        # Write bundle as formatted JSON
        file_path.write_text(json.dumps(bundle_data, indent=2), encoding="utf-8")

        # Return relative path as URI
        return f"file://{file_path.absolute()}"

    def retrieve_bundle(self, storage_uri: str) -> dict:
        """
        Retrieve a FHIR bundle from storage.

        Args:
            storage_uri: Storage URI returned by store_bundle

        Returns:
            FHIR bundle as dictionary

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        # Extract path from URI
        if storage_uri.startswith("file://"):
            file_path = Path(storage_uri.replace("file://", ""))
        else:
            file_path = self.bundle_storage_path / storage_uri

        if not file_path.exists():
            raise FileNotFoundError(f"Bundle not found at {storage_uri}")

        return json.loads(file_path.read_text(encoding="utf-8"))

    def get_pdf_path(self, storage_uri: str) -> Path:
        """
        Get filesystem path for a stored PDF.

        Args:
            storage_uri: Storage URI

        Returns:
            Path object for the file
        """
        if storage_uri.startswith("file://"):
            return Path(storage_uri.replace("file://", ""))
        return self.pdf_storage_path / storage_uri

    def get_bundle_path(self, storage_uri: str) -> Path:
        """
        Get filesystem path for a stored bundle.

        Args:
            storage_uri: Storage URI

        Returns:
            Path object for the file
        """
        if storage_uri.startswith("file://"):
            return Path(storage_uri.replace("file://", ""))
        return self.bundle_storage_path / storage_uri

    def delete_pdf(self, storage_uri: str) -> bool:
        """
        Delete a PDF file from storage.

        Args:
            storage_uri: Storage URI

        Returns:
            True if file was deleted, False if it didn't exist
        """
        file_path = self.get_pdf_path(storage_uri)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def delete_bundle(self, storage_uri: str) -> bool:
        """
        Delete a bundle file from storage.

        Args:
            storage_uri: Storage URI

        Returns:
            True if file was deleted, False if it didn't exist
        """
        file_path = self.get_bundle_path(storage_uri)
        if file_path.exists():
            file_path.unlink()
            return True
        return False


# Singleton instance
_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """Get singleton storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
