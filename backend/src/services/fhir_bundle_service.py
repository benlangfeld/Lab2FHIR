"""FHIR bundle generation service."""

import hashlib
import json
import uuid
from datetime import datetime

from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import (
    DocumentReference,
    DocumentReferenceContent,
    DocumentReferenceContentAttachment,
)
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient, PatientName
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.errors import BundleGenerationError, NotFoundError
from src.db.models import (
    FhirBundleArtifact,
    GenerationMode,
    LabReport,
    ParsedLabDataVersion,
    PatientProfile,
    ValidationStatus,
)
from src.domain.determinism import (
    generate_diagnostic_report_id,
    generate_document_reference_id,
    generate_observation_id,
    hex_to_base64_bytes,
)
from src.domain.fhir_mapping import (
    SYSTEM_LAB2FHIR_FILE_HASH,
    SYSTEM_LAB2FHIR_SUBJECT_ID,
    SYSTEM_LOINC,
    create_codeable_concept,
    create_identifier,
    create_reference,
    format_datetime_for_fhir,
    get_loinc_code_for_analyte,
    map_measurement_to_value,
)
from src.domain.intermediate_schema import ParsedLabData


class FhirBundleService:
    """Service for generating FHIR bundles from parsed lab data."""

    async def generate_bundle(
        self,
        report_id: uuid.UUID,
        db: AsyncSession,
        generation_mode: GenerationMode = GenerationMode.INITIAL,
    ) -> FhirBundleArtifact:
        """
        Generate FHIR transaction bundle for a lab report.

        Args:
            report_id: Report ID
            db: Database session
            generation_mode: Initial or regeneration

        Returns:
            Created bundle artifact

        Raises:
            NotFoundError: If report or dependencies not found
            BundleGenerationError: If bundle generation fails
        """
        try:
            # Get report
            report_result = await db.execute(select(LabReport).where(LabReport.id == report_id))
            report = report_result.scalar_one_or_none()
            if not report:
                raise NotFoundError("LabReport", str(report_id))

            # Get patient
            patient_result = await db.execute(
                select(PatientProfile).where(PatientProfile.id == report.patient_id)
            )
            patient = patient_result.scalar_one_or_none()
            if not patient:
                raise NotFoundError("PatientProfile", str(report.patient_id))

            # Get latest valid parsed version
            parsed_result = await db.execute(
                select(ParsedLabDataVersion)
                .where(
                    ParsedLabDataVersion.report_id == report_id,
                    ParsedLabDataVersion.validation_status == ValidationStatus.VALID,
                )
                .order_by(ParsedLabDataVersion.version_number.desc())
            )
            parsed_version = parsed_result.scalar_one_or_none()
            if not parsed_version:
                raise NotFoundError("ParsedLabDataVersion", f"for report {report_id}")

            # Parse payload
            parsed_data = ParsedLabData(**parsed_version.payload_json)

            # Generate bundle
            bundle_dict = self._create_fhir_bundle(
                patient=patient,
                report=report,
                parsed_data=parsed_data,
            )

            # Calculate bundle hash
            bundle_json_str = json.dumps(bundle_dict, sort_keys=True)
            bundle_hash = hashlib.sha256(bundle_json_str.encode()).hexdigest()

            # Store bundle artifact
            bundle_artifact = FhirBundleArtifact(
                report_id=report_id,
                parsed_version_id=parsed_version.id,
                bundle_json=bundle_dict,
                bundle_hash_sha256=bundle_hash,
                generation_mode=generation_mode,
            )

            db.add(bundle_artifact)
            await db.commit()
            await db.refresh(bundle_artifact)

            return bundle_artifact

        except (NotFoundError, BundleGenerationError):
            raise
        except Exception as e:
            raise BundleGenerationError(
                f"Failed to generate FHIR bundle: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    def _create_fhir_bundle(
        self,
        patient: PatientProfile,
        report: LabReport,
        parsed_data: ParsedLabData,
    ) -> dict:
        """
        Create FHIR transaction bundle.

        Args:
            patient: Patient profile
            report: Lab report
            parsed_data: Parsed lab data

        Returns:
            FHIR bundle as dictionary
        """
        entries = []

        # 1. Patient resource
        patient_resource = self._create_patient_resource(patient)
        entries.append(
            BundleEntry(
                fullUrl=f"urn:uuid:{patient.id}",
                resource=patient_resource,
                request=BundleEntryRequest(method="POST", url="Patient"),
            )
        )

        # 2. DocumentReference resource
        doc_ref_id = generate_document_reference_id(report.file_hash_sha256)
        doc_ref_resource = self._create_document_reference(
            doc_ref_id=doc_ref_id,
            patient_id=str(patient.id),
            report=report,
        )
        entries.append(
            BundleEntry(
                fullUrl=f"DocumentReference/{doc_ref_id}",
                resource=doc_ref_resource,
                request=BundleEntryRequest(method="PUT", url=f"DocumentReference/{doc_ref_id}"),
            )
        )

        # 3. DiagnosticReport resource
        diag_report_id = generate_diagnostic_report_id(
            patient.external_subject_id,
            parsed_data.report_date or datetime.now(),
            report.file_hash_sha256,
        )
        observation_refs = []

        # 4. Observation resources
        for measurement in parsed_data.measurements:
            obs_id = generate_observation_id(
                patient.external_subject_id,
                measurement.collection_datetime,
                measurement.normalized_analyte_code or measurement.original_analyte_name,
                measurement.numeric_value or measurement.qualitative_value,
                measurement.normalized_unit_ucum or measurement.original_unit,
            )
            obs_resource = self._create_observation(
                obs_id=obs_id,
                patient_id=str(patient.id),
                measurement=measurement,
            )
            observation_refs.append(create_reference("Observation", obs_id))
            entries.append(
                BundleEntry(
                    fullUrl=f"Observation/{obs_id}",
                    resource=obs_resource,
                    request=BundleEntryRequest(method="PUT", url=f"Observation/{obs_id}"),
                )
            )

        # Create DiagnosticReport with observation references
        diag_report_resource = self._create_diagnostic_report(
            diag_report_id=diag_report_id,
            patient_id=str(patient.id),
            doc_ref_id=doc_ref_id,
            observation_refs=observation_refs,
            parsed_data=parsed_data,
        )
        entries.append(
            BundleEntry(
                fullUrl=f"DiagnosticReport/{diag_report_id}",
                resource=diag_report_resource,
                request=BundleEntryRequest(
                    method="PUT", url=f"DiagnosticReport/{diag_report_id}"
                ),
            )
        )

        # Create bundle
        bundle = Bundle(
            type="transaction",
            entry=entries,
        )

        return bundle.dict(exclude_none=True)

    def _create_patient_resource(self, patient: PatientProfile) -> Patient:
        """Create FHIR Patient resource."""
        return Patient(
            identifier=[
                create_identifier(SYSTEM_LAB2FHIR_SUBJECT_ID, patient.external_subject_id)
            ],
            name=[PatientName(text=patient.display_name)],
        )

    def _create_document_reference(
        self, doc_ref_id: str, patient_id: str, report: LabReport
    ) -> DocumentReference:
        """Create FHIR DocumentReference resource."""
        return DocumentReference(
            id=doc_ref_id,
            status="current",
            docStatus="final",
            type=create_codeable_concept(
                SYSTEM_LOINC, "11502-2", "Laboratory report", "Laboratory report"
            ),
            subject=create_reference("Patient", patient_id),
            identifier=[create_identifier(SYSTEM_LAB2FHIR_FILE_HASH, report.file_hash_sha256)],
            content=[
                DocumentReferenceContent(
                    attachment=DocumentReferenceContentAttachment(
                        contentType=report.mime_type,
                        title=report.original_filename,
                        hash=hex_to_base64_bytes(report.file_hash_sha256),
                    )
                )
            ],
        )

    def _create_diagnostic_report(
        self,
        diag_report_id: str,
        patient_id: str,
        doc_ref_id: str,
        observation_refs: list,
        parsed_data: ParsedLabData,
    ) -> DiagnosticReport:
        """Create FHIR DiagnosticReport resource."""
        return DiagnosticReport(
            id=diag_report_id,
            status="final",
            code=create_codeable_concept(
                SYSTEM_LOINC, "11502-2", "Laboratory report", "Laboratory report"
            ),
            subject=create_reference("Patient", patient_id),
            effectiveDateTime=(
                format_datetime_for_fhir(parsed_data.report_date)
                if parsed_data.report_date
                else None
            ),
            result=observation_refs,
        )

    def _create_observation(
        self, obs_id: str, patient_id: str, measurement
    ) -> Observation:
        """Create FHIR Observation resource."""
        # Get LOINC code if available
        loinc_code = None
        if measurement.normalized_analyte_code:
            loinc_mapping = get_loinc_code_for_analyte(measurement.normalized_analyte_code)
            if loinc_mapping:
                loinc_code, loinc_display = loinc_mapping
                code_concept = create_codeable_concept(
                    SYSTEM_LOINC,
                    loinc_code,
                    loinc_display,
                    measurement.original_analyte_name,
                )
            else:
                code_concept = create_codeable_concept(
                    "urn:lab2fhir:analyte",
                    measurement.normalized_analyte_code,
                    measurement.original_analyte_name,
                    measurement.original_analyte_name,
                )
        else:
            code_concept = create_codeable_concept(
                "urn:lab2fhir:analyte",
                measurement.original_analyte_name,
                measurement.original_analyte_name,
                measurement.original_analyte_name,
            )

        # Map measurement to FHIR value
        value_fields = map_measurement_to_value(measurement)

        obs = Observation(
            id=obs_id,
            status="final",
            code=code_concept,
            subject=create_reference("Patient", patient_id),
            effectiveDateTime=format_datetime_for_fhir(measurement.collection_datetime),
            issued=(
                format_datetime_for_fhir(measurement.result_datetime)
                if measurement.result_datetime
                else format_datetime_for_fhir(measurement.collection_datetime)
            ),
            **value_fields,
        )

        return obs


def get_fhir_bundle_service() -> FhirBundleService:
    """Get FHIR bundle service instance."""
    return FhirBundleService()
