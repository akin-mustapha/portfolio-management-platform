"""
Bronze Pipeline for Trading212 historical events.

Ingests three cursor-paginated endpoints into separate raw tables:
  - /equity/history/dividends     → raw.t212_history_dividend
  - /equity/history/orders        → raw.t212_history_order
  - /equity/history/transactions  → raw.t212_history_transaction

Per-endpoint high-water marks are stored in raw.t212_history_cursor and used
to stop pagination once a page's oldest event is at or before the last seen
event timestamp, so steady-state runs are cheap under the 6 req/min limit.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

from pipeline.etl.protocols import Source, Destination
from pipeline.etl.policies import Pipeline

from pipeline.etl.loaders.loader_bronze_t212_history import (
    FullLoaderPostgresT212History,
)

from pipeline.infrastructure.clients.api_client_trading212 import Trading212APIClient

from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

_QUERIES_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "queries"

_ENDPOINTS = {
    "dividends": "equity/history/dividends",
    "orders": "equity/history/orders",
    "transactions": "equity/history/transactions",
}

_EVENT_TS_KEY = {
    "dividends": "paidOn",
    "orders": None,  # nested — handled in _item_event_ts
    "transactions": "dateTime",
}


def _parse_ts(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _item_event_ts(endpoint: str, item: dict):
    """Best-effort event timestamp extraction. Returns None if unavailable."""
    if endpoint == "orders":
        order = (item or {}).get("order") or {}
        return _parse_ts(order.get("createdAt"))
    key = _EVENT_TS_KEY.get(endpoint)
    if key is None:
        return None
    return _parse_ts((item or {}).get(key))


# ─────────────────────────────────────────────
# Source
# ─────────────────────────────────────────────


class Trading212HistorySource(Source):
    def __init__(self):
        self._api_client = Trading212APIClient(URL, API_TOKEN, SECRET_TOKEN)
        self._db_client = SQLModelClient(DATABASE_URL)

    def extract(self) -> dict:
        result: dict[str, Any] = {"cursors": {}}

        for endpoint_key, path in _ENDPOINTS.items():
            try:
                stored_ts = self._get_stored_high_water_mark(endpoint_key)
                items, newest_ts, newest_cursor = self._pull_endpoint(
                    endpoint_key, path, stored_ts
                )
                result[endpoint_key] = items
                result["cursors"][endpoint_key] = {
                    "last_cursor": newest_cursor,
                    "last_event_ts": newest_ts or stored_ts,
                }
                logging.info(
                    f"[t212_history:{endpoint_key}] fetched {len(items)} items; "
                    f"new high-water mark: {newest_ts or stored_ts}"
                )
            except Exception as e:
                # Isolate endpoint failures so one broken stream doesn't poison the others.
                logging.exception(
                    f"[t212_history:{endpoint_key}] extraction failed: {e}"
                )
                result[endpoint_key] = []
                result["cursors"][endpoint_key] = {}

        return result

    def _pull_endpoint(self, endpoint_key: str, path: str, stored_ts):
        """Page through endpoint, collecting items newer than stored_ts."""
        collected: list[dict] = []
        newest_ts = None
        newest_cursor = None

        def stop_once_page_is_older(page: dict) -> bool:
            if stored_ts is None:
                return False
            items = page.get("items") or []
            if not items:
                return True
            oldest = min(
                (
                    ts
                    for ts in (_item_event_ts(endpoint_key, i) for i in items)
                    if ts is not None
                ),
                default=None,
            )
            if oldest is None:
                return False
            return oldest <= stored_ts

        for page in self._api_client.iter_paginated(
            endpoint=path,
            stop_predicate=stop_once_page_is_older,
        ):
            items = page.get("items") or []
            for item in items:
                ts = _item_event_ts(endpoint_key, item)
                if stored_ts is not None and ts is not None and ts <= stored_ts:
                    continue  # already seen in a previous run
                collected.append(item)
                if ts is not None and (newest_ts is None or ts > newest_ts):
                    newest_ts = ts

            next_path = page.get("nextPagePath")
            if next_path and "cursor=" in next_path and newest_cursor is None:
                # Stash the first nextPagePath's cursor as opaque observability state.
                newest_cursor = next_path.split("cursor=")[-1].split("&")[0]

        return collected, newest_ts, newest_cursor

    def _get_stored_high_water_mark(self, endpoint_key: str):
        sql = load_query(_QUERIES_DIR / "bronze" / "t212_history_cursor_select.sql")
        with self._db_client as client:
            result = client.execute(sql, params={"endpoint": endpoint_key})
            row = result.fetchone() if result is not None else None
        if row is None:
            return None
        return _parse_ts(getattr(row, "last_event_ts", None))


# ─────────────────────────────────────────────
# Destination
# ─────────────────────────────────────────────


class Trading212HistoryDestination(Destination):
    def load(self, data: Any) -> None:
        FullLoaderPostgresT212History().load(data)


# ─────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────


class PipelineT212History(Pipeline):
    def __init__(self):
        self._source = Trading212HistorySource()
        self._destination = Trading212HistoryDestination()

    def run(self):
        try:
            data = self._source.extract()
            # if not self._has_payload(data):
            #     logging.info("[t212_history] no new events; skipping load")
            #     return None
            self._destination.load(data)
            return None
        except Exception as e:
            raise e

    @staticmethod
    def _has_payload(data: dict) -> bool:
        for key in _ENDPOINTS:
            if data.get(key):
                return True
        return False


if __name__ == "__main__":
    PipelineT212History().run()
