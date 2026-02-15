"""Parsed data API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.errors import NotFoundError
from src.db.models import ParsedLabDataVersion, ValidationStatus
from src.db.session import get_db

router = APIRouter()


class ParsedDataResponse(BaseModel):
    """Response model for parsed lab data."""

    id: uuid.UUID
    report_id: uuid.UUID
    version_number: int
    version_type: str
    schema_version: str
    payload: dict
    validation_status: ValidationStatus
    validation_errors: dict | None = None
    created_by: str
    created_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, parsed_version: ParsedLabDataVersion) -> "ParsedDataResponse":
        """Convert ORM model to response model."""
        return cls(
            id=parsed_version.id,
            report_id=parsed_version.report_id,
            version_number=parsed_version.version_number,
            version_type=parsed_version.version_type.value,
            schema_version=parsed_version.schema_version,
            payload=parsed_version.payload_json,
            validation_status=parsed_version.validation_status,
            validation_errors=parsed_version.validation_errors,
            created_by=parsed_version.created_by,
            created_at=parsed_version.created_at.isoformat(),
        )


@router.get("/{report_id}", response_model=ParsedDataResponse)
async def get_parsed_data(
    report_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ParsedDataResponse:
    """
    Get the latest valid parsed data for a report.

    Args:
        report_id: Report ID
        db: Database session

    Returns:
        Latest parsed data version

    Raises:
        NotFoundError: If no parsed data found for report
    """
    # Get latest valid version
    result = await db.execute(
        select(ParsedLabDataVersion)
        .where(
            ParsedLabDataVersion.report_id == report_id,
            ParsedLabDataVersion.validation_status == ValidationStatus.VALID,
        )
        .order_by(ParsedLabDataVersion.version_number.desc())
    )
    parsed_version = result.scalar_one_or_none()

    if not parsed_version:
        raise NotFoundError("ParsedLabData", f"for report {report_id}")

    return ParsedDataResponse.from_orm(parsed_version)
