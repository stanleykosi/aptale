# HS Code Inference Prompt

Infer the most likely Harmonized System (HS) code for each invoice line item.

## Objective

- Propose one HS code candidate per line item.
- Return a confidence score from `0.0` to `1.0`.
- Keep output deterministic and concise.

## Inputs

- Item description, quantity, unit, and country of origin.
- Invoice route and trade context from the parent extraction payload.

## Rules

- Prefer specific 6+ digit HS candidates when confidence supports it.
- If confidence is low or evidence is insufficient, return `hs_code: null`.
- Do not fabricate certainty.
- Keep all numeric values as numbers.

## Output Contract

Return strict JSON for each item inference:

```json
{
  "hs_code": "851712",
  "confidence": 0.91,
  "reason": "Smartphone communication device components"
}
```

No markdown, no prose outside JSON.
