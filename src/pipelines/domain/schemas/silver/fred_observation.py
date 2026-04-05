from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_validator


class FredObservationRecord(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    series_id: str
    observation_date: date
    value: Decimal
    business_key: str
    ingested_date: date

    @field_validator("series_id", "business_key")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("value")
    @classmethod
    def must_be_finite(cls, v: Decimal) -> Decimal:
        if not v.is_finite():
            raise ValueError("value must be a finite number")
        return v
