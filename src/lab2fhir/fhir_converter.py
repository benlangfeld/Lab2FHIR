"""FHIR R4 resource converter."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import (
    DocumentReference,
    DocumentReferenceContent,
    DocumentReferenceContentProfile,
)
from fhir.resources.attachment import Attachment
from fhir.resources.identifier import Identifier
from fhir.resources.observation import Observation, ObservationReferenceRange
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference

from .normalizers import DateNormalizer, UnitNormalizer
from .schemas import LabReport


class FHIRConverter:
    """Convert parsed lab reports to FHIR R4 resources."""

    def __init__(self):
        """Initialize the converter with normalizers."""
        self.unit_normalizer = UnitNormalizer()
        self.date_normalizer = DateNormalizer()

    def _generate_id(self) -> str:
        """Generate a unique ID for FHIR resources."""
        return str(uuid.uuid4())

    def _ensure_instant_format(self, dt_string: Optional[str]) -> str:
        """
        Ensure datetime string is in FHIR Instant format (with timezone).
        
        Args:
            dt_string: ISO datetime string
            
        Returns:
            FHIR Instant formatted string (YYYY-MM-DDTHH:MM:SS+00:00)
        """
        if not dt_string:
            # Return current UTC time with timezone
            return datetime.now(timezone.utc).isoformat()
        
        # Check if already has timezone info using regex
        # Match Z suffix or timezone offset like +00:00 or -05:00
        import re
        has_timezone = bool(re.search(r'(Z|[+-]\d{2}:\d{2})$', dt_string))
        
        if has_timezone:
            return dt_string
        
        # Add UTC timezone
        return dt_string + '+00:00'

    def _create_patient_reference(self, lab_report: LabReport) -> dict:
        """
        Create a patient reference dictionary.

        Args:
            lab_report: Parsed lab report

        Returns:
            Patient reference dictionary
        """
        reference = {}

        if lab_report.patient_id:
            reference["reference"] = f"Patient/{lab_report.patient_id}"

        if lab_report.patient_name:
            reference["display"] = lab_report.patient_name

        # If no reference data, use a placeholder
        if not reference:
            reference["display"] = "Unknown Patient"

        return reference

    def create_document_reference(
        self, lab_report: LabReport, pdf_base64: str, pdf_filename: str = "lab_report.pdf"
    ) -> DocumentReference:
        """
        Create a FHIR DocumentReference resource with embedded PDF.

        Args:
            lab_report: Parsed lab report
            pdf_base64: Base64 encoded PDF content
            pdf_filename: Name of the PDF file

        Returns:
            FHIR DocumentReference resource
        """
        doc_ref_id = self._generate_id()

        # Normalize report date
        report_date = None
        if lab_report.report_date:
            normalized = self.date_normalizer.normalize_datetime(lab_report.report_date)
            report_date = self._ensure_instant_format(normalized)
        else:
            report_date = self._ensure_instant_format(None)

        # Create attachment with base64 PDF
        attachment = Attachment(
            contentType="application/pdf",
            data=pdf_base64,
            title=pdf_filename,
        )

        # Create content
        content = DocumentReferenceContent(
            attachment=attachment,
        )

        # Create document type coding
        doc_type = CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="11502-2",
                    display="Laboratory report",
                )
            ],
            text="Laboratory Report",
        )

        # Build DocumentReference
        doc_ref = DocumentReference(
            id=doc_ref_id,
            status="current",
            type=doc_type,
            subject=self._create_patient_reference(lab_report),
            date=report_date,
            content=[content],
        )

        return doc_ref

    def create_diagnostic_report(
        self,
        lab_report: LabReport,
        observation_refs: List[str],
        doc_ref_id: Optional[str] = None,
    ) -> DiagnosticReport:
        """
        Create a FHIR DiagnosticReport resource.

        Args:
            lab_report: Parsed lab report
            observation_refs: List of Observation resource IDs
            doc_ref_id: DocumentReference ID to link

        Returns:
            FHIR DiagnosticReport resource
        """
        report_id = self._generate_id()

        # Normalize dates
        effective_date = None
        if lab_report.collection_date:
            effective_date = self.date_normalizer.normalize_datetime(
                lab_report.collection_date
            )
        effective_date = self._ensure_instant_format(effective_date)

        issued_date = None
        if lab_report.report_date:
            issued_date = self.date_normalizer.normalize_datetime(lab_report.report_date)
        issued_date = self._ensure_instant_format(issued_date)

        # Create category
        category = [
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/v2-0074",
                        code="LAB",
                        display="Laboratory",
                    )
                ]
            )
        ]

        # Create code for the report
        code = CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="11502-2",
                    display="Laboratory report",
                )
            ],
            text="Laboratory Report",
        )

        # Create observation references
        result_refs = [Reference(reference=f"Observation/{obs_id}") for obs_id in observation_refs]

        # Build DiagnosticReport
        diagnostic_report = DiagnosticReport(
            id=report_id,
            status="final",
            category=category,
            code=code,
            subject=self._create_patient_reference(lab_report),
            effectiveDateTime=effective_date,
            issued=issued_date,
            result=result_refs if result_refs else None,
        )

        # Add performer if available
        if lab_report.ordering_provider or lab_report.lab_name:
            performer_display = lab_report.ordering_provider or lab_report.lab_name
            diagnostic_report.performer = [
                Reference(display=performer_display)
            ]

        # Link to DocumentReference if provided
        if doc_ref_id:
            diagnostic_report.presentedForm = [
                Attachment(
                    contentType="application/pdf",
                    url=f"DocumentReference/{doc_ref_id}",
                )
            ]

        return diagnostic_report

    def create_observation(
        self,
        result,
        lab_report: LabReport,
        diagnostic_report_ref: Optional[str] = None,
    ) -> Observation:
        """
        Create a FHIR Observation resource from a lab result.

        Args:
            result: LabResult object
            lab_report: Parent lab report
            diagnostic_report_ref: DiagnosticReport ID to link

        Returns:
            FHIR Observation resource
        """
        obs_id = self._generate_id()

        # Normalize collection date
        effective_date = None
        if lab_report.collection_date:
            effective_date = self.date_normalizer.normalize_datetime(
                lab_report.collection_date
            )
        effective_date = self._ensure_instant_format(effective_date)

        # Create category
        category = [
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="laboratory",
                        display="Laboratory",
                    )
                ]
            )
        ]

        # Create code for the observation (using test name)
        code = CodeableConcept(text=result.test_name)

        # Normalize unit
        normalized_unit = self.unit_normalizer.normalize(result.unit)

        # Try to parse value as numeric
        value_quantity = None
        value_string = None

        try:
            # Remove common formatting characters and try to parse as float
            clean_value = result.value.replace(",", "").replace(" ", "").strip()
            numeric_value = float(clean_value)
            value_quantity = Quantity(
                value=numeric_value,
                unit=normalized_unit or result.unit,
                system="http://unitsofmeasure.org",
                code=normalized_unit or result.unit,
            )
        except (ValueError, AttributeError):
            # Not a numeric value, use string
            value_string = result.value

        # Build Observation
        observation = Observation(
            id=obs_id,
            status="final",
            category=category,
            code=code,
            subject=self._create_patient_reference(lab_report),
            effectiveDateTime=effective_date,
        )

        # Set value
        if value_quantity:
            observation.valueQuantity = value_quantity
        else:
            observation.valueString = value_string

        # Add reference range if available
        if result.reference_range:
            ref_range = ObservationReferenceRange(text=result.reference_range)
            observation.referenceRange = [ref_range]

        # Add interpretation if abnormal flag present
        if result.abnormal_flag:
            interpretation_coding = None
            flag_upper = result.abnormal_flag.upper()

            if flag_upper in ["H", "HIGH"]:
                interpretation_coding = Coding(
                    system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    code="H",
                    display="High",
                )
            elif flag_upper in ["L", "LOW"]:
                interpretation_coding = Coding(
                    system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    code="L",
                    display="Low",
                )
            elif flag_upper in ["A", "ABNORMAL"]:
                interpretation_coding = Coding(
                    system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    code="A",
                    display="Abnormal",
                )

            if interpretation_coding:
                observation.interpretation = [
                    CodeableConcept(coding=[interpretation_coding])
                ]

        # Add specimen type if available
        if lab_report.specimen_type:
            observation.specimen = Reference(display=lab_report.specimen_type)

        # Add performer if available
        if lab_report.lab_name:
            observation.performer = [Reference(display=lab_report.lab_name)]

        return observation

    def convert_to_bundle(
        self, lab_report: LabReport, pdf_base64: str, pdf_filename: str = "lab_report.pdf"
    ) -> Bundle:
        """
        Convert a lab report to a FHIR R4 transaction Bundle.

        Args:
            lab_report: Parsed lab report
            pdf_base64: Base64 encoded PDF
            pdf_filename: Name of the PDF file

        Returns:
            FHIR transaction Bundle containing all resources
        """
        bundle_id = self._generate_id()

        # Create DocumentReference
        doc_ref = self.create_document_reference(lab_report, pdf_base64, pdf_filename)

        # Create Observations
        observations = []
        observation_ids = []
        for result in lab_report.results:
            obs = self.create_observation(result, lab_report)
            observations.append(obs)
            observation_ids.append(obs.id)

        # Create DiagnosticReport
        diagnostic_report = self.create_diagnostic_report(
            lab_report, observation_ids, doc_ref.id
        )

        # Build Bundle entries
        entries = []

        # Add DocumentReference entry
        entries.append(
            BundleEntry(
                fullUrl=f"urn:uuid:{doc_ref.id}",
                resource=doc_ref,
                request=BundleEntryRequest(method="POST", url="DocumentReference"),
            )
        )

        # Add DiagnosticReport entry
        entries.append(
            BundleEntry(
                fullUrl=f"urn:uuid:{diagnostic_report.id}",
                resource=diagnostic_report,
                request=BundleEntryRequest(method="POST", url="DiagnosticReport"),
            )
        )

        # Add Observation entries
        for obs in observations:
            entries.append(
                BundleEntry(
                    fullUrl=f"urn:uuid:{obs.id}",
                    resource=obs,
                    request=BundleEntryRequest(method="POST", url="Observation"),
                )
            )

        # Create Bundle
        bundle = Bundle(
            id=bundle_id,
            type="transaction",
            entry=entries,
        )

        return bundle

    def bundle_to_json(self, bundle: Bundle) -> str:
        """
        Convert a FHIR Bundle to JSON string.

        Args:
            bundle: FHIR Bundle resource

        Returns:
            JSON string representation
        """
        return bundle.model_dump_json(indent=2, exclude_none=True)
