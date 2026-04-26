from confluent_kafka import Consumer
import os
from dotenv import load_dotenv
import json
import logging
from datetime import date
from dataclasses import dataclass

from src.services.ingestion.infra.repositories.table_repository_factory import (
    TableRepositoryFactory,
)
from src.shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class QueryRepository:
    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)

    def select_all_asset_not_updated_since(self):
        query = """
        WITH base AS (
            SELECT DISTINCT ON (a.id)
                a.id AS asset_id,
                a.name AS ticker,
                a.name AS name,
                'default' AS asset_type,
                'default' AS exchange,
                s.currency
            FROM portfolio.asset a
            LEFT JOIN portfolio.asset_snapshot s
            ON a.id = s.asset_id
            ORDER BY a.id, s.data_date DESC  -- pick latest snapshot per asset
        )
        INSERT INTO analytics.dim_asset (
            id,
            asset_id,
            ticker,
            name,
            asset_type,
            exchange,
            currency
        )
        SELECT
            gen_random_uuid(),  -- id
            asset_id,
            ticker,
            name,
            asset_type,
            exchange,
            currency
        FROM base
        ON CONFLICT (asset_id) DO UPDATE SET
            ticker = EXCLUDED.ticker,
            name = EXCLUDED.name,
            asset_type = EXCLUDED.asset_type,
            exchange = EXCLUDED.exchange,
            currency = EXCLUDED.currency;
        """
        with self._client as db:
            result = db.execute(query)
            return result

    def calc_asset_price_daily(self):
        # Example query logic for calculating daily asset prices
        query = """
           WITH processed AS (
            SELECT f.asset_id, d.date AS processed_date
            FROM analytics.fact_asset_price_daily f
            JOIN analytics.dim_date d
            ON f.date_id = d.id
        ),
        base AS (
            SELECT
                s.asset_id,
                s.data_date::date AS price_date,
                s.price,
                s.data_date,
                ROW_NUMBER() OVER (
                    PARTITION BY s.asset_id, s.data_date::date
                    ORDER BY s.data_date ASC
                ) AS rn_open,
                ROW_NUMBER() OVER (
                    PARTITION BY s.asset_id, s.data_date::date
                    ORDER BY s.data_date DESC
                ) AS rn_close
            FROM portfolio.asset_snapshot s
            LEFT JOIN processed p
            ON s.asset_id = p.asset_id
            AND s.data_date::date = p.processed_date
            WHERE p.asset_id IS NULL  -- only unprocessed snapshots
        ),
        daily_metrics AS (
            SELECT
                b.asset_id,
                d.id AS date_id,
                AVG(b.price) AS average_price,
                MAX(CASE WHEN b.rn_open  = 1 THEN b.price END) AS opening_price,
                MAX(CASE WHEN b.rn_close = 1 THEN b.price END) AS closing_price,
                MAX(b.price) AS high,
                MIN(b.price) AS low,
                now() AS updated_timestamp
            FROM base b
            JOIN analytics.dim_date d
            ON b.price_date = d.date
            GROUP BY b.asset_id, d.id
        )
        INSERT INTO analytics.fact_asset_price_daily (
            asset_id,
            date_id,
            average_price,
            opening_price,
            closing_price,
            high,
            low,
            updated_timestamp
        )
        SELECT *
        FROM daily_metrics
        WHERE asset_id IS NOT NULL
        ON CONFLICT (asset_id, date_id)
        DO UPDATE SET
            average_price = EXCLUDED.average_price,
            opening_price = EXCLUDED.opening_price,
            closing_price = EXCLUDED.closing_price,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            updated_timestamp = EXCLUDED.updated_timestamp;
        """
        with self._client as db:
            result = db.execute(query)
            return result


# ───────────────────────── Logging ─────────────────────────

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=f"{LOG_DIR}/asset_event_consumer_run.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)


# Domain Policy
@dataclass
class Asset:
    asset_id: str
    date: date
    open_price: float
    close_price: float
    high: float
    low: float
    volume: int
    return_pct: float = None
    risk_level: str = None

    def calculate_metrics(self):
        if self.open_price and self.close_price:
            self.return_pct = (
                (self.close_price - self.open_price) / self.open_price * 100
            )
            self.risk_level = "High" if self.return_pct < -0.05 else "Low"


# ───────────────────────── Consumer ─────────────────────────


class AnalyticsConsumer:
    def __init__(self):
        logging.info("Initializing AnalyticsConsumer")

        self._consumer = Consumer(
            {
                "bootstrap.servers": "localhost:9092",
                "group.id": "discovery-group-1",
                "enable.auto.commit": True,
                # "auto.offset.reset": "earliest",
            }
        )

        self._topics = ["analytics.ingestion"]

        self._query_repo = QueryRepository()
        self._fact_asset_price_daily_repo = TableRepositoryFactory.get(
            "fact_asset_price_daily"
        )

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

        print(event)


# ───────────────────────── Entrypoint ─────────────────────────

if __name__ == "__main__":
    AnalyticsConsumer().run()
