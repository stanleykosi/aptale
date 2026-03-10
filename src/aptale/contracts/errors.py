"""Contract-layer errors for Aptale JSON payload handling."""

from __future__ import annotations


class ContractsError(ValueError):
    """Base class for payload contract errors."""


class SchemaNotFoundError(ContractsError):
    """Raised when a requested schema is unknown or missing on disk."""


class MalformedPayloadError(ContractsError):
    """Raised when payload shape/content is malformed before schema validation."""


class SchemaValidationError(ContractsError):
    """Raised when payload fails JSON Schema validation."""

    def __init__(self, schema_name: str, errors: list[str]) -> None:
        self.schema_name = schema_name
        self.errors = tuple(errors)
        joined = "; ".join(errors)
        super().__init__(f"Payload failed '{schema_name}' schema validation: {joined}")


class NormalizationError(ContractsError):
    """Raised when value normalization fails."""


class PartialPayloadError(ContractsError):
    """Raised when payload is structurally valid but incomplete for calculation."""

