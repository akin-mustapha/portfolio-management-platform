from abc import ABC, abstractmethod
from src.services.ingestion.app.protocols import Source
from src.services.ingestion.app.protocols import Destination
from src.services.ingestion.app.protocols import Transformation

class Pipeline(ABC):
  _source: Source
  _transformation: Transformation
  _destination: Destination
    
  @abstractmethod
  def run(self):
    raise NotImplementedError


