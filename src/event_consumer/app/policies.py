from datetime import datetime, UTC
from abc import ABC, abstractmethod

  
  
class SchemeFactory(ABC):
  @abstractmethod
  def get_schema(self, table_name):
    pass

class Mapper(ABC):
  @abstractmethod
  def map(self) -> None:
    pass
  

class EventConsumer(ABC):
  @abstractmethod
  def run(self, event) -> None:
    pass
  
  
class Repository(ABC):
  def __init__(self, entity_name, schema_name):
    self._entity_name = entity_name
    self._schema_name = schema_name
    
  @property
  def entity_name(self):
    return self._entity_name
  
  @entity_name.setter
  def entity_name(self, entity_name):
    self._entity_name = entity_name
    
  @abstractmethod
  def insert(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def upsert(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def select(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def select_all(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def update(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
  
  @abstractmethod
  def delete(self, **kwargs):
    raise NotImplementedError("Subclasses must implement this method")
