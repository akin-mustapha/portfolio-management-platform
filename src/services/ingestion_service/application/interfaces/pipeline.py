from abc import ABC, abstractmethod
from src.services.ingestion_service.application.interfaces.protocols.destination import Destination
from src.services.ingestion_service.application.interfaces.protocols.source import Source
from src.services.ingestion_service.application.interfaces.protocols.transformation import Transformation


class Pipeline(ABC):
  @abstractmethod
  def run(self):
    raise NotImplementedError