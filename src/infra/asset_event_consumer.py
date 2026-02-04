from confluent_kafka import Consumer
import os
import json
from typing import Dict
from datetime import datetime, UTC
from src.services.ingestion.app.interfaces import Data
from src.shared.repositories.entity_repository import EntityRepository
from src.shared.repositories.raw_data_repository import RawDataRepository
import logging


log_dir_name = 'logs'
os.path.exists(log_dir_name) or os.makedirs(log_dir_name)
logging.basicConfig(
  level=logging.INFO,
  filename=f'{log_dir_name}/asset_event_consumer_run.log',
  filemode='a',
  format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
  )
class Trading212AssetConsumer:
  """
    Trading212AssetConsumer:
  """
  def __init__(self):
    logging.info("Initializing Tradin212AssetConsumer")
    self._consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": "discovery-group-1",
        # "auto.offset.reset": "earliest",
        "enable.auto.commit": True
    })
    self._topic: list[str] = ["asset.ingestion"]
    self._raw_data_repo = RawDataRepository()
    self._asset_repo = EntityRepository("asset")
    self._asset_snapshot_repo = EntityRepository("asset_snapshot")

  def run(self):
    logging.info("Subcribing to topic : %s", self._topic)
    self._consumer.subscribe(self._topic)
    logging.info("Listening for messages…")
    while True:
        msg = self._consumer.poll(3.0)  # 1 second timeout
        if msg is None:
            continue
        if msg.error():
            logging.error("Error:", msg.error())
            continue
        
        logging.info("Decoding Message")
        event = json.loads(msg.value().decode())
        record = event.get("payload", [])
        logging.info("Consuming Asset")
        self._consume_asset(record)
        logging.info("Consuming Asset Snapshot")
        self._consume_asset_snapshot(record)
        logging.info("Saving Raw Data")
        self._to_sink(event)

  def _consume_asset(self, record: list) -> list[Dict]:
    record = self._extract_asset(record)
    self._load_asset(record)

  def _consume_asset_snapshot(self, record: list) -> list[Dict]:
    record = self._extract_asset_snapshot(record)
    self._load_asset_snapshot(record)

  def _extract_asset(self, record):
    """
      _extract: 
    """
    transformed_data = []
    for asset in record:
      instrument = asset.get("instrument", {})
      data = dict(
          # TODO: Map to config
          external_id=instrument.get("ticker"),
          name=instrument.get("ticker"),
          description=instrument.get("name"),
          source_name="trading212",
          is_active=True,
          created_datetime=datetime.now(UTC),
      )
      transformed_data.append(data)
    return transformed_data

  def _extract_asset_snapshot(self, record):
    """
      _extract: 
    """
    data_date = datetime.now(UTC)
    transformed_data = []
    for asset in record:
      instrument = asset.get('instrument', {})
      ticker = instrument.get('ticker', '')
      wallet_impact = asset.get('walletImpact', {})
      record = self._asset_repo.select({'external_id': ticker})
      asset_id = record[0]
      data = {
        "asset_id": asset_id,
        "data_date": data_date,
        "share": asset.get('quantity', 0),
        "price": asset.get('currentPrice', 0),
        "avg_price": asset.get('averagePricePaid', 0),
        "value": wallet_impact.get('currentValue', 0),
        "cost": wallet_impact.get('totalCost', 0),
        "profit": wallet_impact.get('unrealizedProfitLoss', 0),
        "fx_impact": wallet_impact.get('fxImpact', 0),
        "currency": instrument.get('currency', ''),
        "local_currency": wallet_impact.get('currency', ''),
      }
      transformed_data.append(data)
    return transformed_data
     
  def _load_asset(self, record):
     self._asset_repo.upsert(records=record, unique_key='external_id')

  def _load_asset_snapshot(self, record):
     logging.info("Inserting Snapshot Data")
     self._asset_snapshot_repo.insert(records=record)

  def _to_sink(self, event):
    data = {
      "source": event.get('source', ''),
      "payload": json.dumps(event.get('payload', '')),
      "is_processed": 1,
      "created_datetime": datetime.now(UTC),
      "processed_datetime": "",
    }
    logging.info("Inserting raw data")
    self._raw_data_repo.insert(record=data)
     
     
if __name__ == "__main__":
   asset_consumer = Trading212AssetConsumer()
   asset_consumer.run()