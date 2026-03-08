
import os
import logging

from src.services.event_consumer.infra.kafka_adapter import KafkaAdapter
from .trading212_asset_consumer import Trading212AssetConsumer

# ───────────────────────── Logging ─────────────────────────

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=f"{LOG_DIR}/asset_event_consumer_run.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)


if __name__ == "__main__":
  KafkaAdapter().run()