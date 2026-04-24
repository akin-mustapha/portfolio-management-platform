import os
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text

from ....application.policies import FullLoader
from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_QUERIES_DIR = Path(__file__).parent.parent.parent.parent / "infrastructure" / "queries"

_ENDPOINT_TABLES = {
    "dividends": "raw.t212_history_dividend",
    "orders": "raw.t212_history_order",
    "transactions": "raw.t212_history_transaction",
}


class FullLoaderPostgresT212History(FullLoader):
    """
    Loads paginated T212 history (dividends, orders, transactions) into three
    raw tables partitioned by ingested_date, and upserts per-endpoint cursor
    state into raw.t212_history_cursor for incremental pulls.

    Data shape expected by _loader:
        {
            "dividends":    [ {raw_api_item}, ... ],
            "orders":       [ ... ],
            "transactions": [ ... ],
            "cursors": {
                "dividends":    {"last_cursor": str|None, "last_event_ts": datetime|None},
                "orders":       {...},
                "transactions": {...},
            },
        }
    """

    def __init__(self):
        # _table_name is logical — this loader manages three tables.
        super().__init__("raw.t212_history")
        self._client = SQLModelClient(DATABASE_URL)

    def _create_partition(self):
        sql_template = load_query(_QUERIES_DIR / "bronze" / "create_partition.sql")
        with self._client as client:
            for table in _ENDPOINT_TABLES.values():
                partition_name = f"{table}_{self._day}"
                sql = sql_template.format(
                    partition_name=partition_name,
                    table_name=table,
                )
                client.execute(sql, {"day": self._day, "next_day": self._next_day})

    def _loader(self, data: dict):
        ingested_date = datetime.now().date()
        insert_sql_template = load_query(
            _QUERIES_DIR / "bronze" / "t212_history_insert.sql"
        )
        cursor_sql = load_query(
            _QUERIES_DIR / "bronze" / "t212_history_cursor_upsert.sql"
        )

        with self._client as client:
            for endpoint, table in _ENDPOINT_TABLES.items():
                items = data.get(endpoint, []) or []
                if items:
                    insert_sql = insert_sql_template.format(table_name=table)
                    for item in items:
                        row_id = self._extract_id(endpoint, item)
                        if row_id is None:
                            logging.warning(
                                f"[{endpoint}] skipping item without id key: {list(item.keys())}"
                            )
                            continue
                        client.execute(
                            insert_sql,
                            params={
                                "id": str(row_id),
                                "ingested_date": ingested_date,
                                "payload": json.dumps(item),
                            },
                        )

                cursor = (data.get("cursors") or {}).get(endpoint) or {}
                if (
                    cursor.get("last_cursor") is not None
                    or cursor.get("last_event_ts") is not None
                ):
                    client.execute(
                        cursor_sql,
                        params={
                            "endpoint": endpoint,
                            "last_cursor": cursor.get("last_cursor"),
                            "last_event_ts": cursor.get("last_event_ts"),
                        },
                    )

    @staticmethod
    def _extract_id(endpoint: str, item: dict):
        # dividends + transactions: top-level `reference` (string)
        # orders: HistoricalOrder wraps {order, fill} — id is nested under `order`
        if endpoint == "orders":
            return (item.get("order") or {}).get("id")
        return item.get("reference")


    def _exposition_abstraction(self):
        drop_dividend = "DROP VIEW IF EXISTS raw.v_bronze_dividend"
        create_dividend = load_query(_QUERIES_DIR / "bronze" / "v_bronze_dividend.sql").format(
            table_name=_ENDPOINT_TABLES["dividends"]
        )

        drop_order = "DROP VIEW IF EXISTS raw.v_bronze_order"
        create_order = load_query(_QUERIES_DIR / "bronze" / "v_bronze_order.sql").format(
            table_name=_ENDPOINT_TABLES["orders"]
        )

        with self._client.engine.connect() as conn:
            conn.execute(text(drop_dividend))
            conn.execute(text(create_dividend))
            conn.execute(text(drop_order))
            conn.execute(text(create_order))
            conn.commit()
