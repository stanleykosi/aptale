# PII Redactor Hook

This Hermes hook writes sanitized activity log entries for `agent:step` and `agent:end` events.

## What It Redacts

- Supplier/vendor identifiers
- Street-like addresses
- Invoice identifiers and invoice-number patterns
- Raw pricing fields and currency-denominated amounts

Redacted values are replaced with one of:

- `[REDACTED_SUPPLIER]`
- `[REDACTED_ADDRESS]`
- `[REDACTED_INVOICE]`
- `[REDACTED_PRICE]`

The hook sanitizes a deep-copied context payload before log write, so the original runtime context (including WhatsApp response delivery content) is not mutated.

## Files

- `handler.py`: Hook handler with recursive redaction and JSONL activity logging.

## Runtime Registration

Create `~/.hermes/hooks/pii-redactor/HOOK.yaml` with:

```yaml
name: pii-redactor
description: Sanitize PII and raw pricing fields from activity logs
events:
  - agent:step
  - agent:end
```

Hermes loads hooks in gateway mode and calls `handle(event_type, context)` for subscribed events.
