# Language Detection and Translation Prompt

Detect the invoice source language and translate extracted textual fields into the target language provided in context.

## Rules

- Preserve exact numeric values, units, and identifiers (invoice numbers, HS codes, ports, quantities).
- Do not translate codes, currency codes, or country codes.
- Do not infer missing values during translation.
- If source language is ambiguous, choose the best candidate and keep confidence conservative in extraction output.

## Output Coupling

- The final extraction output must include:
  - `source_language` as a BCP-47-like short code (for example `zh`, `tr`, `en`).
  - `target_language` from context.
- Translation is part of extraction; do not emit separate prose.
