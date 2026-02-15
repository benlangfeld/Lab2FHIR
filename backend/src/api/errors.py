"""API error taxonomy and exception handlers."""

from enum import StrEnum
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorCode(StrEnum):
    """Error codes for API responses."""

    # General errors
    INTERNAL_ERROR = "internal_error"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"

    # Upload errors
    INVALID_FILE_TYPE = "invalid_file_type"
    FILE_TOO_LARGE = "file_too_large"
    DUPLICATE_UPLOAD = "duplicate_upload"
    SCANNED_PDF_REJECTED = "scanned_pdf_rejected"

    # Processing errors
    PARSING_FAILED = "parsing_failed"
    SCHEMA_VALIDATION_FAILED = "schema_validation_failed"
    STATE_TRANSITION_ERROR = "state_transition_error"
    BUNDLE_GENERATION_FAILED = "bundle_generation_failed"

    # Resource errors
    REPORT_NOT_FOUND = "report_not_found"
    PATIENT_NOT_FOUND = "patient_not_found"
    PARSED_DATA_NOT_FOUND = "parsed_data_not_found"
    BUNDLE_NOT_FOUND = "bundle_not_found"

    # Configuration errors
    LLM_NOT_CONFIGURED = "llm_not_configured"
    STORAGE_ERROR = "storage_error"


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorDetail


class Lab2FHIRException(Exception):
    """Base exception for Lab2FHIR errors."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(Lab2FHIRException):
    """Validation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class NotFoundError(Lab2FHIRException):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=f"{resource} not found: {identifier}",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier},
        )


class ConflictError(Lab2FHIRException):
    """Conflict error (e.g., duplicate resource)."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code=ErrorCode.CONFLICT,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class DuplicateUploadError(Lab2FHIRException):
    """Duplicate file upload error."""

    def __init__(self, existing_report_id: str, file_hash: str):
        super().__init__(
            code=ErrorCode.DUPLICATE_UPLOAD,
            message="This file has already been uploaded",
            status_code=status.HTTP_409_CONFLICT,
            details={
                "existing_report_id": existing_report_id,
                "file_hash": file_hash,
            },
        )


class ScannedPDFError(Lab2FHIRException):
    """Scanned/image PDF rejection error."""

    def __init__(self):
        super().__init__(
            code=ErrorCode.SCANNED_PDF_REJECTED,
            message="Scanned or image-based PDFs are not supported. Please upload text-based PDF.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class StateTransitionError(Lab2FHIRException):
    """Invalid state transition error."""

    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            code=ErrorCode.STATE_TRANSITION_ERROR,
            message=f"Invalid state transition from {from_status} to {to_status}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"from_status": from_status, "to_status": to_status},
        )


class ParsingError(Lab2FHIRException):
    """PDF parsing error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code=ErrorCode.PARSING_FAILED,
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class BundleGenerationError(Lab2FHIRException):
    """FHIR bundle generation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code=ErrorCode.BUNDLE_GENERATION_FAILED,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


async def lab2fhir_exception_handler(request: Request, exc: Lab2FHIRException) -> JSONResponse:
    """Handle Lab2FHIR custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": exc.detail,
                "details": {},
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "An unexpected error occurred",
                "details": {"error_type": type(exc).__name__},
            }
        },
    )
