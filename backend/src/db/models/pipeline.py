"""ORM models for pipeline stages (parsing, FHIR generation, submission)."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base


class ValidationStatus(str, Enum):
    """Validation status enumeration."""

    VALID = "valid"
    INVALID = "invalid"


class VersionType(str, Enum):
    """Parsed data version type enumeration."""

    ORIGINAL = "original"
    CORRECTED = "corrected"


class GenerationMode(str, Enum):
    """Bundle generation mode enumeration."""

    INITIAL = "initial"
    REGENERATION = "regeneration"


class SubmissionStatus(str, Enum):
    """FHIR submission status enumeration."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class ParsedLabDataVersion(Base):
    """Parsed lab data version entity."""

    __tablename__ = "parsed_lab_data_versions"
    __table_args__ = (
        Index("ix_parsed_versions_report_version", "report_id", "version_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lab_reports.id"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(nullable=False)
    version_type: Mapped[VersionType] = mapped_column(nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    validation_status: Mapped[ValidationStatus] = mapped_column(nullable=False)
    validation_errors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    report: Mapped["LabReport"] = relationship(
        back_populates="parsed_versions", foreign_keys=[report_id]
    )
    edit_history: Mapped[list["EditHistoryEntry"]] = relationship(
        back_populates="parsed_version"
    )
    bundle_artifacts: Mapped[list["FhirBundleArtifact"]] = relationship(
        back_populates="parsed_version"
    )

    def __repr__(self) -> str:
        return f"<ParsedLabDataVersion(id={self.id}, report_id={self.report_id}, version={self.version_number})>"


class EditHistoryEntry(Base):
    """Edit history entry for manual corrections."""

    __tablename__ = "edit_history_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    parsed_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parsed_lab_data_versions.id"), nullable=False
    )
    field_path: Mapped[str] = mapped_column(String(500), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    edited_by: Mapped[str] = mapped_column(String(200), nullable=False)
    edited_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    parsed_version: Mapped["ParsedLabDataVersion"] = relationship(
        back_populates="edit_history"
    )

    def __repr__(self) -> str:
        return f"<EditHistoryEntry(id={self.id}, field={self.field_path})>"


class FhirBundleArtifact(Base):
    """FHIR bundle artifact entity."""

    __tablename__ = "fhir_bundle_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lab_reports.id"), nullable=False
    )
    parsed_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parsed_lab_data_versions.id"), nullable=False
    )
    bundle_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    bundle_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    generation_mode: Mapped[GenerationMode] = mapped_column(
        nullable=False, default=GenerationMode.INITIAL
    )

    # Relationships
    report: Mapped["LabReport"] = relationship(
        back_populates="bundle_artifacts", foreign_keys=[report_id]
    )
    parsed_version: Mapped["ParsedLabDataVersion"] = relationship(
        back_populates="bundle_artifacts"
    )
    submission_records: Mapped[list["SubmissionRecord"]] = relationship(
        back_populates="bundle_artifact"
    )

    def __repr__(self) -> str:
        return f"<FhirBundleArtifact(id={self.id}, report_id={self.report_id})>"


class SubmissionRecord(Base):
    """FHIR submission record entity (P5 optional feature)."""

    __tablename__ = "submission_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bundle_artifact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("fhir_bundle_artifacts.id"), nullable=False
    )
    target_base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        nullable=False, default=SubmissionStatus.PENDING
    )
    attempt_count: Mapped[int] = mapped_column(nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    bundle_artifact: Mapped["FhirBundleArtifact"] = relationship(
        back_populates="submission_records"
    )

    def __repr__(self) -> str:
        return f"<SubmissionRecord(id={self.id}, status={self.status})>"


# Circular import resolution - import LabReport type
from src.db.models.reporting import LabReport  # noqa: E402, F401
