from typing import Dict, Optional, Iterable, Any
from abc import ABC, abstractmethod
  
class Repository(ABC):
  
  def __init__(self, entity_name, schema_name, field_mapping=None):
    
    self._entity_name = f"{schema_name}.{entity_name}" if schema_name else entity_name
    self._schema_name = schema_name
    self._field_mapping = field_mapping
    
  @property
  def entity_name(self):
    return self._entity_name
  
  @entity_name.setter
  def entity_name(self, entity_name):
    self._entity_name = entity_name
    
  @property
  def schema_name(self):
    return self._schema_name
  
  @schema_name.setter
  def schema_name(self, schema_name):
    self._schema_name = schema_name
    
  @abstractmethod
  def insert(self, records: Iterable[Dict]):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def upsert(self, records: Iterable[Dict]):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def select(self, params: Dict):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def select_all(self):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def update(self, records: Dict, params: Dict):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def delete(self, params: Dict):
    raise NotImplementedError("Subclasses must implement this method")

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
