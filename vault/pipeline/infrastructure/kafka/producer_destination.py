import os
from dotenv import load_dotenv
import json

from pipeline.domain import Event
from pipeline.etl.policies import EventDestination

from confluent_kafka import Producer

load_dotenv()

KAFKA_URL = os.getenv("KAFKA_URL")


class Trading212KafkaDestination(EventDestination):
    def __init__(self, destination_name: str):
        super().__init__(destination_name)
        self._url = KAFKA_URL
        self._topic: str = "asset.ingestion"
        self._producer = Producer({"bootstrap.servers": KAFKA_URL})

    def send(self, event: Event):
        self._producer.produce(self._topic, json.dumps(dict(event)))
        self._producer.poll(1.0)
        self._producer.flush()
