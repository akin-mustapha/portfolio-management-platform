from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class AssetRecord(BaseModel):
    """
    Business contract for the staging.asset table.
    Enforces types, coerces numeric types from DB Decimal, and rejects
    records with empty identity fields. Used in _to_records() of the
    silver pipeline — invalid records are logged and skipped.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    data_timestamp: datetime
    external_id: str
    ticker: str
    name: str
    description: str
    broker: str
    currency: str
    local_currency: str
    share: float
    price: float
    avg_price: float
    value: float
    cost: float
    profit: float
    fx_impact: float = 0.0
    business_key: str

    @field_validator("fx_impact", mode="before")
    @classmethod
    def coerce_fx_impact(cls, v):
        return v if v is not None else 0.0

    @field_validator("business_key", "external_id", "ticker")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v
