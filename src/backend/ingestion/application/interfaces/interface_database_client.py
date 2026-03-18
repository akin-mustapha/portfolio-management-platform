from typing import Dict, Optional, Iterable, Any
from abc import ABC, abstractmethod

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
