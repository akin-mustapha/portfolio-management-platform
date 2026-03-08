from typing import Dict, Iterable
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
