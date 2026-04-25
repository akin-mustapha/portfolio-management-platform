"""
Unified Gold Pipeline for Trading212

Refreshes the staging materialised views that hold all window computation
(`v_fred_rfr`, `v_fred_sp500`, `v_asset_metrics`, `v_account_metrics`), then
runs one projection query per fact table. Each query is a thin SELECT that
joins the metrics views with `analytics.dim_asset` / `analytics.dim_portfolio`
and returns exactly the columns its fact table expects.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict

from pipeline.etl.policies import Pipeline
from pipeline.etl.protocols import Source, Destination

from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query
from pipeline.infrastructure.repositories.repository_factory import RepositoryFactory

_QUERIES_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "queries"

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
portfolio_id = 21641310


# ---------------------------------------------------------------------------
# Source — refresh views + load per-fact SQL
# ---------------------------------------------------------------------------


_MATERIALIZED_VIEWS = [
    "staging.v_fred_rfr",
    "staging.v_fred_sp500",
    "staging.v_asset_metrics",
    "staging.v_account_metrics",
]


class T212GoldSource(Source):
    """Refreshes the staging metrics views. Queries themselves live on each destination."""

    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)

    def extract(self):
        with self._client as db:
            for view in _MATERIALIZED_VIEWS:
                db.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}")


# ---------------------------------------------------------------------------
# Destinations — each owns its SQL and its repository
# ---------------------------------------------------------------------------


class _FactDestination(Destination):
    """
    Base for fact destinations. Subclasses declare fact_name, sql_file, unique_key.
    """

    fact_name: str
    sql_file: str
    unique_key: List[str]

    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)
        self._repository = RepositoryFactory.get(
            self.fact_name, schema_name="analytics"
        )
        self._sql = load_query(_QUERIES_DIR / "gold" / self.sql_file)

    def load(self, _: Dict = None) -> None:
        with self._client as db:
            rows = db.execute(
                self._sql, params={"portfolio_id": str(portfolio_id)}
            ).fetchall()
        records = [dict(row._mapping) for row in rows]
        if not records:
            logging.warning(f"[t212_gold:{self.fact_name}] NO RECORDS — skipping")
            return
        self._repository.upsert(records=records, unique_key=self.unique_key)


class FactPriceDestination(_FactDestination):
    fact_name = "fact_price"
    sql_file = "fact_price.sql"
    unique_key = ["date_id", "asset_id"]


class FactValuationDestination(_FactDestination):
    fact_name = "fact_valuation"
    sql_file = "fact_valuation.sql"
    unique_key = ["date_id", "asset_id"]


class FactReturnDestination(_FactDestination):
    fact_name = "fact_return"
    sql_file = "fact_return.sql"
    unique_key = ["date_id", "asset_id"]


class FactTechnicalDestination(_FactDestination):
    fact_name = "fact_technical"
    sql_file = "fact_technical.sql"
    unique_key = ["date_id", "asset_id"]


class FactSignalDestination(_FactDestination):
    fact_name = "fact_signal"
    sql_file = "fact_signal.sql"
    unique_key = ["date_id", "asset_id"]


class FactPortfolioDailyDestination(_FactDestination):
    fact_name = "fact_portfolio_daily"
    sql_file = "fact_portfolio_daily.sql"
    unique_key = ["date_id", "portfolio_id"]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


class PipelineT212Gold(Pipeline):
    _pipeline_name = "t212_gold"

    def __init__(self):
        self._db = SQLModelClient(DATABASE_URL)
        self._source = T212GoldSource()
        self._destinations = [
            FactPriceDestination(),
            FactValuationDestination(),
            FactReturnDestination(),
            FactTechnicalDestination(),
            FactSignalDestination(),
            FactPortfolioDailyDestination(),
        ]

    def run(self):
        self._ensure_dimensions()
        self._source.extract()
        for destination in self._destinations:
            destination.load()

    def _ensure_dimensions(self):
        with self._db as db:
            db.execute(load_query(_QUERIES_DIR / "gold" / "dim_portfolio_seed.sql"))
            db.execute(load_query(_QUERIES_DIR / "gold" / "dim_asset_seed.sql"))


if __name__ == "__main__":
    PipelineT212Gold().run()
