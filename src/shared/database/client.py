import os
import json
import logging
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from sqlmodel import SQLModel, create_engine, Session, text
from typing import Any, Dict, List, Optional, Tuple, AsyncIterable

class DatabaseClient(ABC):
    """Abstract base class for database clients."""
    @abstractmethod
    def connect(self) -> Any:
        """Establish a connection to the database."""
        pass
    @abstractmethod
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
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
        logging.info(f"Initializing SQLModelClient with database URL: {database_url}")
        self.engine = create_engine(database_url, echo=echo)
        logging.info("Creating database tables if they do not exist")
        SQLModel.metadata.create_all(self.engine)
        self.session = None

    def connect(self) -> None:
        self.session = Session(self.engine)

    def close(self) -> None:
        if self.session:
            self.session.close()

    def execute(self, query: str, params=None):
        if not self.session:
            raise RuntimeError("Database session is not established.")
        result = None
        try:
            with self.session as s:
                result = s.exec(text(query), params=params or {})
                s.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            raise       
        return result

    def insert(self, table: str, records: Iterable[dict]) -> None:
        if not self.session:
            raise RuntimeError("Database session is not established.")
        for record in records:
            logging.debug(f"Preparing to insert record into {table}")
            column_names = ", ".join(record.keys())
            placeholders = ", ".join(f":{key}" for key in record.keys())
            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
            logging.debug(f"Executing query: {sql} with params: {record}")
            self.execute(sql, record)
            logging.info(f"Inserted record into {table}")

if __name__ == "__main__":
    # example usage
    db_url = "sqlite:///./data/database/test.db"
    client = SQLModelClient(db_url, echo=True)

    with client as db_client:
        db_client.execute("CREATE TABLE IF NOT EXISTS test_2 (id INTEGER, name TEXT)")
        db_client.insert("test", [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
        result = db_client.execute("SELECT * FROM test")
        for row in result:
            print(row)