# Aptale Privacy Notice & Retention Policy

This policy defines the canonical privacy response Aptale sends in WhatsApp:

1. On first invoice upload.
2. When a user asks how invoice data is handled.

## Sensitive Data Boundaries

- Supplier names, invoice identifiers, and raw pricing are sensitive.
- Sensitive invoice details must not be written to broad operational logs.
- Hermes activity logging is protected by `pii-redactor`, which sanitizes `agent:step` and `agent:end` event context before persistence.
- Durable memory (`USER.md`, `MEMORY.md`) is restricted to broker preferences and non-PII operational context.

## Operational Retention Interval

- Canonical current-state retention interval: **7 days** for sanitized operational activity logs.
- Flushing expectation: logs older than 7 days should be rotated/removed on the ops schedule.
- If retention policy changes, update both:
  - `src/aptale/formatters/privacy_notice.py`
  - this document

## User-Facing Privacy Response Scope

The privacy response must clearly state:

- Sensitive boundaries (what is protected and redacted).
- Retention/flushing expectations for operational logs.
- How the user can request the privacy notice again in chat.

All responses remain WhatsApp-native and must avoid exposing supplier names or raw pricing values in logs.
