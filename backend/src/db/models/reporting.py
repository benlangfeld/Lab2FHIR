"""ORM models for patient profiles and lab reports."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base


class SubjectType(str, Enum):
    """Subject type enumeration."""

    HUMAN = "human"
    VETERINARY = "veterinary"


class ReportStatus(str, Enum):
    """Lab report status enumeration."""

    UPLOADED = "uploaded"
    PARSING = "parsing"
    REVIEW_PENDING = "review_pending"
    EDITING = "editing"
    GENERATING_BUNDLE = "generating_bundle"
    REGENERATING_BUNDLE = "regenerating_bundle"
    COMPLETED = "completed"
    FAILED = "failed"
    DUPLICATE = "duplicate"


class PatientProfile(Base):
    """Patient profile entity."""

    __tablename__ = "patient_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_subject_id: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    subject_type: Mapped[SubjectType] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    lab_reports: Mapped[list["LabReport"]] = relationship(back_populates="patient")

    def __repr__(self) -> str:
        return f"<PatientProfile(id={self.id}, external_subject_id={self.external_subject_id})>"


class LabReport(Base):
    """Lab report entity."""

    __tablename__ = "lab_reports"
    __table_args__ = (Index("ix_lab_reports_file_hash", "file_hash_sha256"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patient_profiles.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, default="application/pdf")
    file_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    pdf_storage_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(nullable=False, default=ReportStatus.UPLOADED)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_duplicate_of_report_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lab_reports.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    patient: Mapped["PatientProfile"] = relationship(back_populates="lab_reports")
    parsed_versions: Mapped[list["ParsedLabDataVersion"]] = relationship(
        back_populates="report", foreign_keys="ParsedLabDataVersion.report_id"
    )
    bundle_artifacts: Mapped[list["FhirBundleArtifact"]] = relationship(
        back_populates="report", foreign_keys="FhirBundleArtifact.report_id"
    )
    duplicate_of: Mapped["LabReport | None"] = relationship(
        remote_side="LabReport.id", foreign_keys=[is_duplicate_of_report_id]
    )

    def __repr__(self) -> str:
        return f"<LabReport(id={self.id}, status={self.status}, filename={self.original_filename})>"


# Import to ensure all models are registered
from src.db.models.pipeline import (  # noqa: E402, F401
    EditHistoryEntry,
    FhirBundleArtifact,
    ParsedLabDataVersion,
    SubmissionRecord,
)
