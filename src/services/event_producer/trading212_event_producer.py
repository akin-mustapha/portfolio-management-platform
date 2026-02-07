import logging
from dataclasses import replace
from datetime import datetime, UTC

from .policies import Source
from .policies import Destination
from .policies import EventProducer
from .domain import Event


logging.basicConfig(level="INFO", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class Trading212EventProducer(EventProducer):
  def __init__(self, source: Source, destination: Destination):
    logging.info("="*45)
    logging.info("Initializing Trading212EventProducer")
    logging.info("="*45)
    self._source = source
    self._destination = destination
  def run(self):
    try:
      # fetch from source
      data = self._source.fetch()
      event = Event(producer_name="trading212_event", payload=data.payload, datetime=datetime.now(UTC))  
      # Save to Destination
      self._destination.send(event)
      return None
    except Exception as e:
      # Update raw data
      raw_data = replace(raw_data, is_processed=False)
      # Persist raw data
      self._sink.save(raw_data)

      raise e