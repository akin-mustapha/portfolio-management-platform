import logging
from confluent_kafka import Consumer
from ...application.runners.events.trading212_asset_consumer import (
    Trading212AssetConsumer,
)
import json

logging.basicConfig(level="INFO")


class KafkaAdapter:
    def __init__(self):
        self._consumer = Consumer(
            {
                "bootstrap.servers": "localhost:9092",
                "group.id": "discovery-group-1",
                "enable.auto.commit": True,
                # "auto.offset.reset": "earliest",
            }
        )
        self._subscribe_to_topic = ["asset.ingestion"]

    def run(self):
        self._consumer.subscribe(self._subscribe_to_topic)
        logging.info("Subscribed to topics: %s", self._subscribe_to_topic)
        logging.info("Listening...")
        while True:
            msg = self._consumer.poll(3.0)
            if msg is None:
                continue
            if msg.error():
                logging.error("Kafka error: %s", msg.error())
                continue

            try:
                event = json.loads(msg.value().decode())
            except json.JSONDecodeError as e:
                logging.error("Failed to decode message: %s", e)
                return

            payload = event.get("payload")

            Trading212AssetConsumer().run(payload)
