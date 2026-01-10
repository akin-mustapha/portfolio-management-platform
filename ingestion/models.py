from sqlmodel import SQLModel, Field
from datetime import datetime


class raw_data(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    source: str
    payload: str
    created_datetime: datetime = Field(default_factory=datetime.utcnow)