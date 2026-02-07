import logging
from dataclasses import replace
from datetime import datetime, UTC

from .policies import Origin
from .policies import Destination
from .policies import EventProducer
from .domain import Event


logging.basicConfig(level="INFO", filemode="w", file_name="trading212_event_producer.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(level="DEBUG", filemode="w", filename="trading212_event_producer.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
class Trading212EventProducer(EventProducer):
  def __init__(self, origin: Origin, destination: Destination):
    logging.info("="*45)
    logging.info("Initializing Trading212EventProducer")
    logging.info(f"Origin: {origin.origin_name}")
    logging.info(f"Destination: {destination.destination_name}")
    logging.info("="*45)
    self._origin = origin
    self._destination = destination
    
  def run(self):
    """
    Docstring for run
    
    :param self: Description
  
    """
    logging.info("="*45)
    logging.info("Running Trading212EventProducer")
    logging.info("="*45)
    
    try:
      # fetch from origin
      logging.info("Fetching data from origin")
      event = self._origin.fetch()
      logging.info("Data fetched from origin")
      logging.info(f"Sending event to destination: {dict(replace(event, payload='xxxx'))}")
      # Save to Destination
      self._destination.send(event)
      logging.info("Event sent to destination")
      return None
    except Exception as e:
      logging.error(f"Error in Trading212EventProducer: {e}")
      raise e