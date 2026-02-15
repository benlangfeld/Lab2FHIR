"""Patient profile API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.errors import NotFoundError, ValidationError
from src.db.models import PatientProfile, SubjectType
from src.db.session import get_db

router = APIRouter()


class CreatePatientRequest(BaseModel):
    """Request model for creating a patient profile."""

    external_subject_id: str = Field(..., min_length=1, max_length=200)
    display_name: str = Field(..., min_length=1, max_length=200)
    subject_type: SubjectType


class PatientResponse(BaseModel):
    """Response model for patient profile."""

    id: uuid.UUID
    external_subject_id: str
    display_name: str
    subject_type: SubjectType
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, patient: PatientProfile) -> "PatientResponse":
        """Convert ORM model to response model."""
        return cls(
            id=patient.id,
            external_subject_id=patient.external_subject_id,
            display_name=patient.display_name,
            subject_type=patient.subject_type,
            created_at=patient.created_at.isoformat(),
            updated_at=patient.updated_at.isoformat(),
        )


class PatientListResponse(BaseModel):
    """Response model for list of patients."""

    patients: list[PatientResponse]
    total: int


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    request: CreatePatientRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PatientResponse:
    """
    Create a new patient profile.

    Args:
        request: Patient creation request
        db: Database session

    Returns:
        Created patient profile

    Raises:
        ValidationError: If external_subject_id already exists
    """
    # Check if external_subject_id already exists
    existing = await db.execute(
        select(PatientProfile).where(
            PatientProfile.external_subject_id == request.external_subject_id
        )
    )
    if existing.scalar_one_or_none():
        raise ValidationError(
            f"Patient with external_subject_id '{request.external_subject_id}' already exists",
            details={"field": "external_subject_id", "value": request.external_subject_id},
        )

    # Create new patient
    patient = PatientProfile(
        external_subject_id=request.external_subject_id.strip(),
        display_name=request.display_name.strip(),
        subject_type=request.subject_type,
    )

    db.add(patient)
    await db.commit()
    await db.refresh(patient)

    return PatientResponse.from_orm(patient)


@router.get("", response_model=PatientListResponse)
async def list_patients(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PatientListResponse:
    """
    List all patient profiles.

    Args:
        db: Database session

    Returns:
        List of patient profiles
    """
    result = await db.execute(select(PatientProfile).order_by(PatientProfile.created_at.desc()))
    patients = result.scalars().all()

    return PatientListResponse(
        patients=[PatientResponse.from_orm(p) for p in patients],
        total=len(patients),
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PatientResponse:
    """
    Get a patient profile by ID.

    Args:
        patient_id: Patient ID
        db: Database session

    Returns:
        Patient profile

    Raises:
        NotFoundError: If patient not found
    """
    result = await db.execute(select(PatientProfile).where(PatientProfile.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise NotFoundError("PatientProfile", str(patient_id))

    return PatientResponse.from_orm(patient)
