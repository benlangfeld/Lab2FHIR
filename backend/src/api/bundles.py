"""Bundle API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.errors import NotFoundError
from src.db.models import FhirBundleArtifact, LabReport, ReportStatus
from src.db.session import get_db
from src.domain.report_state_machine import validate_transition
from src.services.fhir_bundle_service import FhirBundleService, get_fhir_bundle_service

router = APIRouter()


class BundleResponse(BaseModel):
    """Response model for bundle artifact."""

    id: uuid.UUID
    report_id: uuid.UUID
    bundle_hash_sha256: str
    generated_at: str
    generation_mode: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, bundle: FhirBundleArtifact) -> "BundleResponse":
        """Convert ORM model to response model."""
        return cls(
            id=bundle.id,
            report_id=bundle.report_id,
            bundle_hash_sha256=bundle.bundle_hash_sha256,
            generated_at=bundle.generated_at.isoformat(),
            generation_mode=bundle.generation_mode.value,
        )


@router.post("/{report_id}/generate", response_model=BundleResponse, status_code=status.HTTP_201_CREATED)
async def generate_bundle(
    report_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    bundle_service: Annotated[FhirBundleService, Depends(get_fhir_bundle_service)],
) -> BundleResponse:
    """
    Generate a FHIR bundle for a report.

    Args:
        report_id: Report ID
        db: Database session
        bundle_service: FHIR bundle service

    Returns:
        Created bundle artifact

    Raises:
        NotFoundError: If report not found
    """
    # Get report
    result = await db.execute(select(LabReport).where(LabReport.id == report_id))
    report = result.scalar_one_or_none()

    if not report:
        raise NotFoundError("LabReport", str(report_id))

    # Transition to generating_bundle
    validate_transition(report.status, ReportStatus.GENERATING_BUNDLE)
    report.status = ReportStatus.GENERATING_BUNDLE
    await db.commit()

    try:
        # Generate bundle
        bundle_artifact = await bundle_service.generate_bundle(report_id, db)

        # Transition to completed
        validate_transition(report.status, ReportStatus.COMPLETED)
        report.status = ReportStatus.COMPLETED
        await db.commit()

        return BundleResponse.from_orm(bundle_artifact)

    except Exception as e:
        # Mark as failed
        report.status = ReportStatus.FAILED
        report.error_code = "bundle_generation_failed"
        report.error_message = str(e)
        await db.commit()
        raise


@router.get("/{report_id}/download")
async def download_bundle(
    report_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JSONResponse:
    """
    Download the FHIR bundle for a report.

    Args:
        report_id: Report ID
        db: Database session

    Returns:
        FHIR bundle as JSON

    Raises:
        NotFoundError: If report or bundle not found
    """
    # Get latest bundle for report
    result = await db.execute(
        select(FhirBundleArtifact)
        .where(FhirBundleArtifact.report_id == report_id)
        .order_by(FhirBundleArtifact.generated_at.desc())
    )
    bundle_artifact = result.scalar_one_or_none()

    if not bundle_artifact:
        raise NotFoundError("FhirBundleArtifact", f"for report {report_id}")

    # Return bundle JSON with appropriate headers
    return JSONResponse(
        content=bundle_artifact.bundle_json,
        headers={
            "Content-Disposition": f'attachment; filename="bundle_{report_id}.json"',
            "Content-Type": "application/fhir+json",
        },
    )
