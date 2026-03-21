from typing import Type

from pydantic import BaseModel, ValidationError

from ..protocols import RejectedRecord, ValidationResult


class SchemaValidator:
    """
    Generic schema validator. Validates a list of raw dicts against a Pydantic model.
    Returns a ValidationResult with typed model instances (valid) and RejectedRecords (invalid).
    pipeline_name is set to None here — the pipeline sets it before writing to dead letter.
    """

    def __init__(self, model: Type[BaseModel], layer: str = "silver"):
        self._model = model
        self._layer = layer

    def validate(self, data: list[dict]) -> ValidationResult:
        valid, invalid = [], []
        for row in data:
            try:
                valid.append(self._model(**row))
            except ValidationError as e:
                invalid.append(RejectedRecord(
                    pipeline_name=None,
                    layer=self._layer,
                    business_key=row.get("business_key"),
                    raw_payload=row,
                    error_type="schema_validation",
                    error_message=str(e),
                ))
        return ValidationResult(valid=valid, invalid=invalid)
