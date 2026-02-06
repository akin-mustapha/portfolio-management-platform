import logging
from typing import List, Any
from dataclasses import replace
from datetime import datetime, UTC
from src.app.interfaces.ingestion import Sink
from src.app.interfaces.ingestion import Source
from src.app.interfaces.ingestion import Destination
from src.app.interfaces.ingestion import Transformation
from src.app.interfaces.ingestion import Pipeline


logging.basicConfig(level="INFO")

class Trading212IngestionPipeline(Pipeline):
  def __init__(self,
               source: Source,
               transformation: Transformation,
               destination: Destination, 
               sink: Sink
               ):
    self._source = source
    self._transformation = transformation
    self._destination = destination
    self._sink = sink
  def run(self):
    # Fetch raw data from source
    raw_data = self._source.fetch()
    # Copy to prevent mutating object
    try:
      # Apply Transformation Logic
      transformed_data: List[Any] = self._transformation.apply_to(raw_data)
      # Save to Destination Table
      self._destination.save(transformed_data)
      # Update raw data
      raw_data = replace(raw_data, is_processed=True)
      raw_data = replace(raw_data, processed_timestamp=datetime.now(UTC))
      self._sink.save(raw_data)
      return None
    except Exception as e:
      # Update raw data
      raw_data = replace(raw_data, is_processed=False)
      # Persist raw data
      self._sink.save(raw_data)

      raise e