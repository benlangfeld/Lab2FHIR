<!--
Sync Impact Report
- Version change: template-placeholder → 1.0.0
- Modified principles:
	- Template Principle 1 → I. Deterministic Transformations
	- Template Principle 2 → II. Validated Intermediate Schema
	- Template Principle 3 → III. PDF Preservation & FHIR Traceability
	- Template Principle 4 → IV. PHI-Safe, Self-Hosted Operation
	- Template Principle 5 → V. Minimal Infrastructure, Replaceable Components
- Added sections:
	- Technical Standards
	- Delivery Workflow & Quality Gates
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ updated: .specify/templates/plan-template.md
	- ✅ updated: .specify/templates/spec-template.md
	- ✅ updated: .specify/templates/tasks-template.md
	- ⚠ pending (not present): .specify/templates/commands/*.md
- Follow-up TODOs:
	- TODO(COMMAND_TEMPLATES): Create .specify/templates/commands/ if command-level guidance is needed.
-->

# Lab2FHIR Constitution

## Core Principles

### I. Deterministic Transformations
All ingestion and conversion behavior MUST be deterministic for identical inputs.
Normalization, deduplication keys, and FHIR generation MUST produce stable results across runs.
Heuristic or probabilistic behavior MAY be used only in parsing, and MUST be followed by
strict validation and deterministic normalization before output is accepted.
Rationale: Stable transformations prevent duplicate or contradictory clinical records.

### II. Validated Intermediate Schema
The system MUST use a strict intermediate JSON model as the contract between extraction/parsing
and FHIR conversion. Direct LLM-to-FHIR generation is prohibited. Every pipeline run MUST pass
schema validation before normalization and before FHIR bundle creation.
Rationale: The intermediate contract decouples model output from clinical resource assembly.

### III. PDF Preservation & FHIR Traceability
Every successful ingestion MUST preserve the source lab PDF and maintain traceability from
derived FHIR resources back to the source document and collection context. Generated bundles
MUST include a DocumentReference and deterministic identifiers for observations.
Rationale: Clinical auditability requires preserving source evidence and provenance linkage.

### IV. PHI-Safe, Self-Hosted Operation
Lab2FHIR MUST remain operable in self-hosted environments with configurable LLM usage.
No feature may force dependence on a vendor-hosted clinical platform. Configuration MUST allow
sensitive data handling controls (API keys, endpoints, auth tokens) via environment settings.
Rationale: The project exists to support privacy-preserving personal and household workflows.

### V. Minimal Infrastructure, Replaceable Components
Solutions MUST prefer the smallest viable operational footprint and avoid unnecessary services.
Components with external coupling (LLM provider, FHIR store, transport layers) MUST be designed
for replacement through clear interfaces and configuration, not hard-coded assumptions.
Rationale: Minimal infrastructure improves portability and long-term maintainability.

## Technical Standards

- Python is the implementation baseline; runtime and tooling choices MUST remain compatible with
	project constraints documented in repo guidance.
- Unit normalization MUST target UCUM-compatible canonical values where mappings exist.
- Date and datetime outputs MUST be ISO 8601; FHIR instant fields MUST include timezone.
- Bundle generation MUST target FHIR R4 transaction bundles containing at least
	DocumentReference, DiagnosticReport, and Observation resources for lab data.
- Deduplication identifiers MUST remain deterministic and based on subject, collection date,
	normalized analyte identity, value, and unit.

## Delivery Workflow & Quality Gates

- Specs, plans, and tasks MUST include an explicit Constitution Check before implementation.
- Feature specs MUST define independent user stories, measurable success criteria, and edge cases.
- Implementation plans MUST identify how constitutional principles are satisfied or justify any
	temporary deviation in a dedicated complexity/exception log.
- Task lists MUST include validation work for schema integrity, normalization behavior,
	deterministic deduplication, and source PDF preservation when those behaviors are affected.
- Pull requests MUST include evidence that relevant tests and lint checks pass before merge.

## Governance

This constitution supersedes conflicting process guidance in this repository.

Amendment procedure:
- Amendments MUST be proposed in a pull request that includes rationale, impact, and any template
	or workflow changes required to preserve consistency.
- At least one maintainer approval is required for ratification of amendments.
- Amendment adoption MUST update dependent templates in `.specify/templates/` in the same change,
	or record explicit follow-up TODOs in the Sync Impact Report.

Versioning policy (semantic):
- MAJOR: Removes or materially redefines a principle or governance requirement.
- MINOR: Adds a new principle/section or materially expands mandatory guidance.
- PATCH: Clarifies language without changing normative meaning.

Compliance review expectations:
- Every plan and PR review MUST evaluate constitutional compliance explicitly.
- Exceptions MUST be documented with scope, rationale, mitigation, and sunset criteria.
- Runtime implementation guidance remains in `.github/copilot-instructions.md` and project docs,
	but MUST not contradict this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-02-14 | **Last Amended**: 2026-02-14
