from src.services.ingestion_service.application.interfaces.pipeline import Pipeline
from src.services.ingestion_service.application.interfaces.protocols.destination import Destination
from src.services.ingestion_service.application.interfaces.protocols.source import Source
from src.services.ingestion_service.application.interfaces.protocols.transformation import Transformation


class Trading212AssetPipeline(Pipeline):
  def __init__(self, source: Source, destination: Destination, transformation: Transformation):
    self._source = source
    self._transformation = transformation
    self._destination = destination
  def run(self):
    raw_data = self._source.fetch()
    transformed_data = self._transformation.apply_to(raw_data)
    self._destination.save(transformed_data)