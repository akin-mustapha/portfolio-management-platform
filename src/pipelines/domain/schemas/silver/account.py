from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class AccountRecord(BaseModel):
    """
    Business contract for the staging.account table.
    Enforces types, coerces numeric types from DB Decimal, and rejects
    records with empty identity fields. Used in _to_records() of the
    silver pipeline — invalid records are logged and skipped.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    data_timestamp: datetime
    external_id: str
    cash_in_pies: float
    cash_available_to_trade: float
    cash_reserved_for_orders: float
    broker: str
    currency: str
    total_value: float
    investments_total_cost: float
    investments_realized_pnl: float
    investments_unrealized_pnl: float
    business_key: str

    @field_validator("business_key", "external_id", "currency")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v
