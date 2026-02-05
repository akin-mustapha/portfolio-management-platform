from confluent_kafka import Consumer
import os
import json
import logging
from typing import Dict, List
from datetime import datetime, UTC

from src.infra.repositories.table_repository_factory import TableRepositoryFactory


# ───────────────────────── Logging ─────────────────────────

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=f"{LOG_DIR}/asset_event_consumer_run.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)


# ───────────────────────── Consumer ─────────────────────────

class Trading212AssetConsumer:
    def __init__(self):
        logging.info("Initializing Trading212AssetConsumer")

        self._consumer = Consumer({
            "bootstrap.servers": "localhost:9092",
            "group.id": "discovery-group-1",
            "enable.auto.commit": True,
            # "auto.offset.reset": "earliest",
        })

        self._topics = ["asset.ingestion"]

        self._raw_data_repo = TableRepositoryFactory.get("raw_data")
        self._asset_repo = TableRepositoryFactory.get("asset")
        self._asset_snapshot_repo = TableRepositoryFactory.get("asset_snapshot")

    # ───────────────────────── Runtime ─────────────────────────

    def run(self):
        self._consumer.subscribe(self._topics)
        logging.info("Subscribed to topics: %s", self._topics)

        while True:
            msg = self._consumer.poll(3.0)

            if msg is None:
                continue

            if msg.error():
                logging.error("Kafka error: %s", msg.error())
                continue

            self._handle_message(msg)

    def _handle_message(self, msg):
        try:
            event = json.loads(msg.value().decode())
        except json.JSONDecodeError as e:
            logging.error("Failed to decode message: %s", e)
            return

        payload = event.get("payload")

        # ─── API Error Handling ───
        if isinstance(payload, dict):
            error = payload.get("error")
            if error:
                logging.error("API Error: %s", error)
                self._save_raw(event, processed=False)
                return

            logging.error("Unexpected dict payload without error field")
            self._save_raw(event, processed=False)
            return

        # ─── Schema Validation ───
        if not isinstance(payload, list):
            logging.error("Invalid payload type: %s", type(payload))
            self._save_raw(event, processed=False)
            return

        # ─── Process Domain Data ───
        try:
            assets = self._extract_assets(payload)
            self._load_assets(assets)

            snapshots = self._extract_asset_snapshots(payload)
            self._load_asset_snapshots(snapshots)

            self._save_raw(event, processed=True)

        except Exception as e:
            logging.exception("Processing failure")
            self._save_raw(event, processed=False)

    # ───────────────────────── Assets ─────────────────────────

    def _extract_assets(self, payload: List[dict]) -> List[Dict]:
        now = datetime.now(UTC)
        records = []

        for item in payload:
            instrument = item.get("instrument", {})

            records.append({
                "external_id": instrument.get("ticker"),
                "name": instrument.get("ticker"),
                "description": instrument.get("name"),
                "source_name": "trading212",
                "is_active": True,
                "created_datetime": now,
            })

        return records

    def _load_assets(self, records: List[Dict]):
        if not records:
            return

        logging.info("Upserting %d assets", len(records))
        self._asset_repo.upsert(data=records, unique_key="external_id")

    # ───────────────────────── Snapshots ─────────────────────────

    def _extract_asset_snapshots(self, payload: List[dict]) -> List[Dict]:
        now = datetime.now(UTC)
        snapshots = []

        for item in payload:
            instrument = item.get("instrument", {})
            ticker = instrument.get("ticker")

            asset_rows = self._asset_repo.select({"external_id": ticker})
            if not asset_rows:
                logging.error("Asset not found for ticker %s", ticker)
                continue

            asset_id = asset_rows[0]
            wallet = item.get("walletImpact", {})

            snapshots.append({
                "asset_id": asset_id,
                "data_date": now,
                "share": item.get("quantity", 0),
                "price": item.get("currentPrice", 0),
                "avg_price": item.get("averagePricePaid", 0),
                "value": wallet.get("currentValue", 0),
                "cost": wallet.get("totalCost", 0),
                "profit": wallet.get("unrealizedProfitLoss", 0),
                "fx_impact": wallet.get("fxImpact", 0),
                "currency": instrument.get("currency", ""),
                "local_currency": wallet.get("currency", ""),
            })

        return snapshots

    def _load_asset_snapshots(self, records: List[Dict]):
        if not records:
            return

        logging.info("Inserting %d asset snapshots", len(records))
        self._asset_snapshot_repo.insert(data=records)

    # ───────────────────────── Raw Sink ─────────────────────────

    def _save_raw(self, event: dict, processed: bool):
        now = datetime.now(UTC)

        self._raw_data_repo.insert({
            "source": event.get("source", ""),
            "payload": json.dumps(event.get("payload")),
            "is_processed": processed,
            "created_datetime": now,
            "processed_datetime": now if processed else None,
        })


# ───────────────────────── Entrypoint ─────────────────────────

if __name__ == "__main__":
    Trading212AssetConsumer().run()