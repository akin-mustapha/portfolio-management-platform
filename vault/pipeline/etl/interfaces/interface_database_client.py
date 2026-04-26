from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any


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
