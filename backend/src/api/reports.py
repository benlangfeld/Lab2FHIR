"""Report API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.errors import DuplicateUploadError, NotFoundError, ValidationError
from src.db.models import LabReport, PatientProfile, ReportStatus
from src.db.session import get_db
from src.domain.determinism import calculate_file_hash
from src.services.report_pipeline_service import ReportPipelineService, get_report_pipeline_service
from src.services.storage_service import get_storage_service

router = APIRouter()


class ReportResponse(BaseModel):
    """Response model for lab report."""

    id: uuid.UUID
    patient_id: uuid.UUID
    original_filename: str
    file_hash_sha256: str
    status: ReportStatus
    error_code: str | None = None
    error_message: str | None = None
    is_duplicate_of_report_id: uuid.UUID | None = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, report: LabReport) -> "ReportResponse":
        """Convert ORM model to response model."""
        return cls(
            id=report.id,
            patient_id=report.patient_id,
            original_filename=report.original_filename,
            file_hash_sha256=report.file_hash_sha256,
            status=report.status,
            error_code=report.error_code,
            error_message=report.error_message,
            is_duplicate_of_report_id=report.is_duplicate_of_report_id,
            created_at=report.created_at.isoformat(),
            updated_at=report.updated_at.isoformat(),
        )


class ReportListResponse(BaseModel):
    """Response model for list of reports."""

    reports: list[ReportResponse]
    total: int


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_report(
    patient_id: Annotated[uuid.UUID, Form()],
    file: Annotated[UploadFile, File()],
    db: Annotated[AsyncSession, Depends(get_db)],
    pipeline: Annotated[ReportPipelineService, Depends(get_report_pipeline_service)],
) -> ReportResponse:
    """
    Upload a lab report PDF.

    Args:
        patient_id: ID of the patient this report belongs to
        file: PDF file upload
        db: Database session
        pipeline: Pipeline service

    Returns:
        Created lab report

    Raises:
        ValidationError: If file type is invalid or patient doesn't exist
        DuplicateUploadError: If file hash already exists
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise ValidationError(
            "Invalid file type. Only PDF files are accepted.",
            details={"content_type": file.content_type},
        )

    # Verify patient exists
    patient_result = await db.execute(select(PatientProfile).where(PatientProfile.id == patient_id))
    patient = patient_result.scalar_one_or_none()
    if not patient:
        raise NotFoundError("PatientProfile", str(patient_id))

    # Read file content
    content = await file.read()

    # Calculate file hash
    file_hash = calculate_file_hash(content)

    # Check for duplicate
    duplicate_result = await db.execute(
        select(LabReport).where(LabReport.file_hash_sha256 == file_hash)
    )
    existing_report = duplicate_result.scalar_one_or_none()

    if existing_report:
        # Create duplicate record
        duplicate_report = LabReport(
            patient_id=patient_id,
            original_filename=file.filename or "unknown.pdf",
            mime_type="application/pdf",
            file_hash_sha256=file_hash,
            pdf_storage_uri=existing_report.pdf_storage_uri,  # Point to same file
            status=ReportStatus.DUPLICATE,
            is_duplicate_of_report_id=existing_report.id,
        )
        db.add(duplicate_report)
        await db.commit()
        await db.refresh(duplicate_report)

        raise DuplicateUploadError(str(existing_report.id), file_hash)

    # Store PDF
    storage = get_storage_service()
    storage_uri = storage.store_pdf(content, file.filename or "unknown.pdf", file_hash)

    # Create report record
    report = LabReport(
        patient_id=patient_id,
        original_filename=file.filename or "unknown.pdf",
        mime_type="application/pdf",
        file_hash_sha256=file_hash,
        pdf_storage_uri=storage_uri,
        status=ReportStatus.UPLOADED,
    )

    db.add(report)
    await db.commit()
    await db.refresh(report)

    # Trigger processing pipeline (fire and forget for now)
    # In production, this would be a background task
    try:
        await pipeline.process_report(report.id, db)
        await db.refresh(report)
    except Exception:
        # Processing error - report is already marked as failed by pipeline
        await db.refresh(report)

    return ReportResponse.from_orm(report)


@router.get("", response_model=ReportListResponse)
async def list_reports(
    patient_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> ReportListResponse:
    """
    List lab reports, optionally filtered by patient.

    Args:
        patient_id: Optional patient ID to filter by
        db: Database session

    Returns:
        List of lab reports
    """
    query = select(LabReport).order_by(LabReport.created_at.desc())

    if patient_id:
        query = query.where(LabReport.patient_id == patient_id)

    result = await db.execute(query)
    reports = result.scalars().all()

    return ReportListResponse(
        reports=[ReportResponse.from_orm(r) for r in reports],
        total=len(reports),
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReportResponse:
    """
    Get a lab report by ID.

    Args:
        report_id: Report ID
        db: Database session

    Returns:
        Lab report

    Raises:
        NotFoundError: If report not found
    """
    result = await db.execute(select(LabReport).where(LabReport.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise NotFoundError("LabReport", str(report_id))

    return ReportResponse.from_orm(report)
