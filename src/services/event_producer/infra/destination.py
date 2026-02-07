import os
from dotenv import load_dotenv
import json

from ..domain import Event
from ..policies import Destination

from confluent_kafka import Producer


load_dotenv()

KAFKA_URL = os.getenv("KAFKA_URL")

class Trading212KafkaDestination(Destination):
  def __init__(self, destination_name: str):
    super().__init__(destination_name)
    self._url = KAFKA_URL
    self._topic: str = "asset.ingestion"
  def send(self, event: Event):
    kafka_producer = Producer({
          "bootstrap.servers": "localhost:9092"
      })
    
    kafka_producer.produce(self._topic, json.dumps(dict(event)))
    kafka_producer.poll(1.0)
    kafka_producer.flush()
    kafka_producer.close()