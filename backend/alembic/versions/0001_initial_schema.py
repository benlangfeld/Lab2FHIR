"""Initial schema for core tables and indexes

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-02-15 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create patient_profiles table
    op.create_table(
        "patient_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("external_subject_id", sa.String(length=200), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column(
            "subject_type",
            sa.Enum("human", "veterinary", name="subjecttype", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_subject_id"),
    )

    # Create lab_reports table
    op.create_table(
        "lab_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("pdf_storage_uri", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "uploaded",
                "parsing",
                "review_pending",
                "editing",
                "generating_bundle",
                "regenerating_bundle",
                "completed",
                "failed",
                "duplicate",
                name="reportstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("is_duplicate_of_report_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patient_profiles.id"]),
        sa.ForeignKeyConstraint(["is_duplicate_of_report_id"], ["lab_reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lab_reports_file_hash", "lab_reports", ["file_hash_sha256"])

    # Create parsed_lab_data_versions table
    op.create_table(
        "parsed_lab_data_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "version_type",
            sa.Enum("original", "corrected", name="versiontype", native_enum=False),
            nullable=False,
        ),
        sa.Column("schema_version", sa.String(length=20), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "validation_status",
            sa.Enum("valid", "invalid", name="validationstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("validation_errors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_by", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["lab_reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_parsed_versions_report_version",
        "parsed_lab_data_versions",
        ["report_id", "version_number"],
    )

    # Create edit_history_entries table
    op.create_table(
        "edit_history_entries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("parsed_version_id", sa.Uuid(), nullable=False),
        sa.Column("field_path", sa.String(length=500), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("edited_by", sa.String(length=200), nullable=False),
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["parsed_version_id"], ["parsed_lab_data_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create fhir_bundle_artifacts table
    op.create_table(
        "fhir_bundle_artifacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_id", sa.Uuid(), nullable=False),
        sa.Column("parsed_version_id", sa.Uuid(), nullable=False),
        sa.Column("bundle_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("bundle_hash_sha256", sa.String(length=64), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "generation_mode",
            sa.Enum("initial", "regeneration", name="generationmode", native_enum=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["parsed_version_id"], ["parsed_lab_data_versions.id"]),
        sa.ForeignKeyConstraint(["report_id"], ["lab_reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create submission_records table (P5 optional)
    op.create_table(
        "submission_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("bundle_artifact_id", sa.Uuid(), nullable=False),
        sa.Column("target_base_url", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "success", "failed", name="submissionstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["bundle_artifact_id"], ["fhir_bundle_artifacts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("submission_records")
    op.drop_table("fhir_bundle_artifacts")
    op.drop_table("edit_history_entries")
    op.drop_index("ix_parsed_versions_report_version", table_name="parsed_lab_data_versions")
    op.drop_table("parsed_lab_data_versions")
    op.drop_index("ix_lab_reports_file_hash", table_name="lab_reports")
    op.drop_table("lab_reports")
    op.drop_table("patient_profiles")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS submissionstatus")
    op.execute("DROP TYPE IF EXISTS generationmode")
    op.execute("DROP TYPE IF EXISTS validationstatus")
    op.execute("DROP TYPE IF EXISTS versiontype")
    op.execute("DROP TYPE IF EXISTS reportstatus")
    op.execute("DROP TYPE IF EXISTS subjecttype")
