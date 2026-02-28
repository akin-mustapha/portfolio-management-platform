from abc import ABC, abstractmethod
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


