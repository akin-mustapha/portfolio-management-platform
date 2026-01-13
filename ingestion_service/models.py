from sqlmodel import SQLModel, Field
from datetime import datetime


class raw_data(SQLModel, table=True):
    # __table_args__ = {'schema': 'stg'}
    id: int = Field(default=None, primary_key=True)
    source: str
    payload: str
    is_processed: bool = Field(default=False)
    created_datetime: datetime = Field(default_factory=datetime.utcnow)
    processed_datetime: datetime | None = None


class asset(SQLModel, table=True):
    # __table_args__ = {'schema': 'app'}
    id: int = Field(default=None, primary_key=True)
    external_id: str = Field(index=True)
    name: str
    description: str
    source_name: str
    created_datetime: datetime = Field(default_factory=datetime.utcnow)
    updated_datetime: datetime | None = Field(default_factory=datetime.utcnow)