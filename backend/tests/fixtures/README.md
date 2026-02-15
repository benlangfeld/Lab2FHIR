# Test Fixtures

This directory contains synthetic test data for the Lab2FHIR converter.

## Structure

```
fixtures/
├── README.md (this file)
├── us1/              # User Story 1: Basic upload and processing
│   ├── lab_numeric_basic.pdf
│   ├── lab_numeric_basic_expected.json
│   └── lab_numeric_basic_fhir_expected.json
├── us2/              # User Story 2: Manual corrections
├── us3/              # User Story 3: Duplicate detection
├── us4/              # User Story 4: Unit normalization
└── shared/           # Common test data and utilities
```

## Fixture Naming Convention

- `{test_name}.pdf` - Source PDF file
- `{test_name}_expected.json` - Expected intermediate parsed representation
- `{test_name}_fhir_expected.json` - Expected FHIR bundle output

## Creating Fixtures

All fixtures must be:
1. **Synthetic**: No real patient data or PHI
2. **Deterministic**: Same input always produces same output
3. **Documented**: Include expected outputs for validation
4. **Minimal**: Focus on specific test scenarios

## Fixture Coverage Matrix

| Scenario | Fixture | Description |
|----------|---------|-------------|
| Basic numeric labs | `us1/lab_numeric_basic.pdf` | Simple lab with numeric values |
| Qualitative results | TBD | Labs with qualitative values (e.g., "Positive") |
| Operator-based values | TBD | Labs with <, >, <=, >= operators |
| Multi-measurement panels | TBD | Labs with multiple related measurements |
| Duplicate uploads | `us3/duplicate_*.pdf` | Same file uploaded twice |
| Mixed units | `us4/mixed_units_*.pdf` | Same analyte in different units |
