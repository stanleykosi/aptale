# Invoice Fixture Set

Synthetic fixtures for Aptale batch evaluation of:

- invoice extraction
- extraction clarification/correction
- routing readiness
- fail-fast intake behavior

These fixtures intentionally avoid real supplier identities, customer names, or live pricing records.

## Files

- `sample_en.json`: English invoice fixture (happy path).
- `sample_cn.json`: Chinese-language invoice fixture (translated extraction path).
- `sample_tr.json`: Turkish-language invoice fixture (translated extraction path).
- `sample_fr.json`: French-language invoice fixture (translated extraction path).
- `sample_hi.json`: Hindi-language invoice fixture (translated extraction path).
- `sample_pt.json`: Portuguese-language invoice fixture (translated extraction path).
- `blurry_failure.json`: Failure-case fixture for blurry/unreadable invoice intake.
- `missing_route_failure.json`: Failure-case fixture for missing route details.
- `unreadable_totals_failure.json`: Failure-case fixture for unreadable invoice totals.
- `uncertain_hs_failure.json`: Failure-case fixture for uncertain HS classification.

## Fixture Shape

Each fixture file contains:

- `fixture_version`: fixture contract version.
- `fixture_id`: stable fixture identifier.
- `case_type`: `success` or `failure`.
- `language`: source invoice language.
- `whatsapp_event`: canonical WhatsApp image event payload used by intake orchestration.
- `invoice_text_lines`: OCR-like invoice lines (synthetic).
- `expected_invoice_extraction`: canonical extraction payload shape for successful cases.
- `clarification`: confirmation/correction reply examples for clarify flow testing.
- `routing_expectations`: minimal route/currency context expected before delegation.

Failure fixtures contain:

- `mock_extraction_payload`: degraded extraction payload used to test fail-fast detectors.
- `expected_failure`: expected failure code and operator-facing recovery hints.

## Evaluation Dataset

`data/eval_invoices.jsonl` references these fixtures for Hermes batch-runner prompts.

Hermes batch-processing contract requires a `prompt` field on each JSONL line. The dataset uses that shape so it can be executed directly by `batch_runner.py`.

Current synthetic coverage:

- Languages: `en`, `zh`, `tr`, `fr`, `hi`, `pt`.
- Lanes: CN->NG, TR->NG, FR->NG, IN->NG, BR->NG.
- Failure classes: `blurry_image`, `missing_route`, `unreadable_totals`, `uncertain_hs_code`.
