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