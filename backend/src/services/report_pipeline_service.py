"""Report pipeline orchestration service."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.errors import NotFoundError
from src.api.errors import StateTransitionError as StateTransitionAPIError
from src.db.models import (
    LabReport,
    ParsedLabDataVersion,
    ReportStatus,
    ValidationStatus,
    VersionType,
)
from src.domain.intermediate_schema import ParsedLabData
from src.domain.report_state_machine import StateTransitionError, validate_transition
from src.services.parser_service import ParserService, get_parser_service
from src.services.pdf_extraction_service import PDFExtractionService, get_pdf_extraction_service


class ReportPipelineService:
    """Service for orchestrating report processing pipeline."""

    def __init__(
        self,
        pdf_extraction: PDFExtractionService | None = None,
        parser: ParserService | None = None,
    ):
        """Initialize pipeline service."""
        self.pdf_extraction = pdf_extraction or get_pdf_extraction_service()
        self.parser = parser or get_parser_service()

    async def process_report(
        self,
        report_id: uuid.UUID,
        db: AsyncSession,
    ) -> LabReport:
        """
        Process a report through the pipeline: extract text -> parse -> store.

        Args:
            report_id: ID of the report to process
            db: Database session

        Returns:
            Updated lab report

        Raises:
            NotFoundError: If report not found
            StateTransitionError: If invalid state transition
        """
        # Get report
        result = await db.execute(select(LabReport).where(LabReport.id == report_id))
        report = result.scalar_one_or_none()

        if not report:
            raise NotFoundError("LabReport", str(report_id))

        try:
            # Transition to parsing
            validate_transition(report.status, ReportStatus.PARSING)
            report.status = ReportStatus.PARSING
            await db.commit()

            # Extract text from PDF
            from src.services.storage_service import get_storage_service

            storage = get_storage_service()
            pdf_content = storage.retrieve_pdf(report.pdf_storage_uri)
            text = self.pdf_extraction.extract_text(pdf_content)

            # Parse text to intermediate schema
            parsed_data = await self.parser.parse_lab_report(text)

            # Store parsed version
            _parsed_version = await self._store_parsed_version(
                report_id=report.id,
                parsed_data=parsed_data,
                db=db,
            )

            # Transition to review_pending
            validate_transition(report.status, ReportStatus.REVIEW_PENDING)
            report.status = ReportStatus.REVIEW_PENDING
            await db.commit()
            await db.refresh(report)

            return report

        except StateTransitionError as e:
            raise StateTransitionAPIError(report.status.value, str(e)) from e
        except Exception as e:
            # Mark as failed
            report.status = ReportStatus.FAILED
            report.error_code = "processing_error"
            report.error_message = str(e)
            await db.commit()
            raise

    async def _store_parsed_version(
        self,
        report_id: uuid.UUID,
        parsed_data: ParsedLabData,
        db: AsyncSession,
    ) -> ParsedLabDataVersion:
        """
        Store parsed data version.

        Args:
            report_id: Report ID
            parsed_data: Parsed lab data
            db: Database session

        Returns:
            Created parsed version
        """
        # Check if this is the first version
        result = await db.execute(
            select(ParsedLabDataVersion)
            .where(ParsedLabDataVersion.report_id == report_id)
            .order_by(ParsedLabDataVersion.version_number.desc())
        )
        existing_versions = result.scalars().all()
        version_number = len(existing_versions) + 1

        # Create new version
        parsed_version = ParsedLabDataVersion(
            report_id=report_id,
            version_number=version_number,
            version_type=VersionType.ORIGINAL,
            schema_version=parsed_data.schema_version,
            payload_json=parsed_data.model_dump(mode="json"),
            validation_status=ValidationStatus.VALID,
            created_by="system",
        )

        db.add(parsed_version)
        await db.commit()
        await db.refresh(parsed_version)

        return parsed_version


def get_report_pipeline_service() -> ReportPipelineService:
    """Get report pipeline service instance."""
    return ReportPipelineService()
