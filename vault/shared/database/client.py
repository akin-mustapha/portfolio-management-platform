import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from sqlalchemy import Engine
from sqlmodel import create_engine, text

# One engine per database URL — avoids repeated create_engine() calls across repositories.
_engines: dict[str, Engine] = {}


def _get_engine(database_url: str, echo: bool = False) -> Engine:
    if database_url not in _engines:
        _engines[database_url] = create_engine(database_url, echo=echo)
    return _engines[database_url]


class DatabaseClient(ABC):
    """Abstract base class for database clients."""

    @abstractmethod
    def connect(self) -> Any:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def execute(self, query: str, params: dict[str, Any] | None = None) -> Any:
        """Execute a SQL query."""
        pass

    @abstractmethod
    def insert(self, table: str, records: Iterable[dict]) -> None:
        """Insert data into a specified table."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    def __enter__(self) -> "DatabaseClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # Propagate exceptions if any


class SQLModelClient(DatabaseClient):
    """SQLModel client for database operations."""

    def __init__(self, database_url: str, echo: bool = False):
        super().__init__()
        self.engine = _get_engine(database_url, echo=echo)

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def execute(self, query: str, params=None):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                rows = result.fetchall() if result.returns_rows else []
                conn.commit()
            return rows
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise

    def insert(self, table: str, records: Iterable[dict]) -> None:
        for record in records:
            logging.debug(f"Preparing to insert record into {table}")
            column_names = ", ".join(record.keys())
            placeholders = ", ".join(f":{key}" for key in record.keys())
            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
            self.execute(sql, record)
            logging.info(f"Inserted record into {table}")
