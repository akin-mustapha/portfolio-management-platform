import json
from datetime import datetime, UTC

from confluent_kafka import Producer
from src.kafka.trading212_asset_source import Trading212AssetSource

class AssetEventProducer:
    def __init__(self):
      # Connect to your Kafka broker
      self._producer = Producer({
          "bootstrap.servers": "localhost:9092"
      })
      self.source = Trading212AssetSource()
      self._topic: str = "asset.ingestion"
    def run(self):
      data = self.source.fetch()
      event = {
          "source": "Trading 212",
          "endpoint": "Trading 212",
          "payload": data,
          "data_datetime": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
      }
      self._producer.produce(self._topic, json.dumps(event))
      self._producer.poll(1.0)
      self._producer.flush()
      self._producer.close()