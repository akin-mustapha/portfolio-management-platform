from abc import ABC, abstractmethod
from datetime import date, timedelta, datetime

from ..app.protocols import Source
from ..app.protocols import Destination
from ..app.protocols import Transformation

class Pipeline(ABC):
  _source: Source
  _transformation: Transformation
  _destination: Destination
    
  @abstractmethod
  def run(self):
    raise NotImplementedError

class FullLoader(ABC):
  def __init__(self, table_name):
    self._current_datetime = datetime.now()
    self._day = self._current_datetime.strftime('%Y_%m_%d')
    self._next_day = (self._current_datetime + timedelta(days=1)).strftime('%Y_%m_%d')
    self._table_name = table_name
    self._partition_name = f"{self._table_name}_{self._day}" 
    
  def load(self, data):
    self._create_partition()
    self._loader(data)
    self._exposition_abstraction()
    
  @abstractmethod
  def _create_partition(self):
    pass
  
  @abstractmethod
  def _loader(self):
    pass
  
  def _exposition_abstraction(self):
    pass