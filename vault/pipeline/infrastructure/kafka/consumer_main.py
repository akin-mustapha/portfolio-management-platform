import logging
import os

from pipeline.infrastructure.kafka.consumer_adapter import KafkaAdapter

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
