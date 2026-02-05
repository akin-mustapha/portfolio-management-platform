from typing import Protocol
from abc import ABC, abstractmethod

class Calc(ABC):
  @abstractmethod
  def run(self):
    raise NotImplementedError

class Query(Protocol):
  def get(self):
    raise NotImplementedError
  
class Func(Protocol):
  def run(self, data):
    raise NotImplementedError
  
class Sink(Protocol):
  def save(self, record):
    raise NotImplementedError
  


class BaseRepositoryInterface(ABC):
    def __init__(self, entity_name, schema_name):
        self._entity_name = entity_name
        self._schema_name = schema_name
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