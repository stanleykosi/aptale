# Execute-Code Contract For Landed Cost

This document defines the canonical Step 28 contract for Aptale's landed-cost
`execute_code` path.

## Purpose

- Run deterministic landed-cost math from canonical JSON input.
- Create a file artifact in the workspace.
- Print exactly the absolute output file path to stdout for downstream
  attachment delivery.

## Canonical Module Surface

- `src/aptale/codegen/landed_cost_script.py`
  - `render_landed_cost_execute_code_script(...)`:
    returns Python script text for Hermes `execute_code`.
  - `compute_and_export_landed_cost(...)`:
    local utility used by tests and orchestration code.
- `src/aptale/codegen/export_helpers.py`
  - `export_landed_cost_payload(...)`:
    writes the artifact and returns an absolute `Path`.

## Required Behavior

- Input must satisfy `landed_cost_input` validation rules.
- Calculation must use deterministic local logic only via
  `aptale.calc.landed_cost.calculate_landed_cost`.
- Output artifact path must be absolute.
- Output directory must be absolute and is expected to be `/workspace` in Hermes
  execution environments.
- Script must not call external APIs directly.
- Script must print only the absolute output file path that was written.

## Export Format In Step 28

- Supported format: `json` only.
- CSV/PDF export implementations are handled in later steps.

## Failure Policy

- Fail fast on malformed input, non-absolute output directory, or unsupported
  export format.
- Do not add fallback behaviors or compatibility shims.
