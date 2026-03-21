import os
import logging
from dotenv import load_dotenv
from typing import List, Dict

from ...application.policies import BaseGoldPipeline
from ...application.protocols import Source, Destination, Transformation
from ...application.validators.schema_validator import SchemaValidator

from shared.database.client import SQLModelClient
from ...infrastructure.repositories.repository_factory import RepositoryFactory
from ...infrastructure.repositories.dead_letter_destination import DeadLetterDestination
from ...domain.schemas.gold.asset_gold import AssetGoldRecord

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ---------------------------------------------------------------------------
# Source
# ---------------------------------------------------------------------------

class AssetGoldSource(Source):
    """
    Queries the latest staging snapshot per asset and joins dim tables for
    surrogate keys. Requires dim_portfolio and dim_asset to be seeded first
    (handled by PipelineAssetGold._ensure_dimensions).
    """

    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)

    def extract(self):
        sql = """
            WITH cte_asset AS (
                SELECT
                    ROW_NUMBER() OVER (
                        PARTITION BY ticker, data_timestamp::DATE
                        ORDER BY data_timestamp DESC
                    ) AS rn,
                    *
                FROM staging.asset
            )
            SELECT
                TO_CHAR(a.data_timestamp, 'YYYYMMDD')::INTEGER  AS date_id,
                dp.id                                             AS portfolio_id,
                da.asset_id,

                a.price,
                a.avg_price,

                a.value,
                a.cost                                            AS cost_basis,
                a.profit                                          AS unrealized_pnl,
                a.profit / NULLIF(a.cost, 0) * 100               AS unrealized_pnl_pct,
                NULL::FLOAT                                       AS realized_pnl,
                c.position_weight_pct,
                a.fx_impact,

                c.daily_return,
                c.cumulative_return,

                c.pct_drawdown,
                c.value_high,
                c.value_low,
                c.ma_20d,
                c.ma_30d,
                c.ma_50d,
                c.volatility_20d,
                c.volatility_30d,
                c.volatility_50d,
                c.var_95_1d,
                c.profit_range_30d,
                c.recent_profit_high_30d,
                c.recent_profit_low_30d,
                c.recent_value_high_30d,
                c.recent_value_low_30d,

                c.dca_bias,
                c.ma_crossover_signal,
                (a.price > c.ma_20d)                             AS price_above_ma_20d,
                (a.price > c.ma_50d)                             AS price_above_ma_50d

            FROM cte_asset a
            JOIN staging.asset_computed c
                ON c.asset_id = a.id
            JOIN analytics.dim_asset da
                ON da.ticker = a.ticker
            CROSS JOIN (
                SELECT id
                FROM analytics.dim_portfolio
                WHERE portfolio_id = 'trading212'
            ) dp
            WHERE a.rn = 1
        """
        with self._client as db:
            result = db.execute(sql)
        return result.fetchall()


# ---------------------------------------------------------------------------
# Transformation
# ---------------------------------------------------------------------------

class AssetGoldTransformation(Transformation):
    """
    Converts SQLAlchemy Row objects from the source into plain dicts.
    Computation is already done in staging.asset_computed — nothing to derive here.
    """

    def transform(self, data: list) -> list[Dict]:
        return [dict(row._mapping) for row in data]


# ---------------------------------------------------------------------------
# Destinations — each projects only the columns its fact table needs
# ---------------------------------------------------------------------------

class FactPriceDestination(Destination):
    _COLUMNS = {'date_id', 'asset_id', 'portfolio_id', 'price', 'avg_price'}

    def __init__(self):
        self._repository = RepositoryFactory.get("fact_price", schema_name="analytics")

    def load(self, data: List[Dict]) -> None:
        records = [{k: v for k, v in r.items() if k in self._COLUMNS} for r in data]
        self._repository.upsert(records=records, unique_key=['date_id', 'asset_id'])


class FactValuationDestination(Destination):
    _COLUMNS = {
        'date_id', 'asset_id', 'portfolio_id',
        'value', 'cost_basis', 'unrealized_pnl', 'unrealized_pnl_pct',
        'realized_pnl', 'position_weight_pct', 'fx_impact',
    }

    def __init__(self):
        self._repository = RepositoryFactory.get("fact_valuation", schema_name="analytics")

    def load(self, data: List[Dict]) -> None:
        records = [{k: v for k, v in r.items() if k in self._COLUMNS} for r in data]
        self._repository.upsert(records=records, unique_key=['date_id', 'asset_id'])


class FactReturnDestination(Destination):
    _COLUMNS = {'date_id', 'asset_id', 'portfolio_id', 'daily_return', 'cumulative_return'}

    def __init__(self):
        self._repository = RepositoryFactory.get("fact_return", schema_name="analytics")

    def load(self, data: List[Dict]) -> None:
        records = [{k: v for k, v in r.items() if k in self._COLUMNS} for r in data]
        self._repository.upsert(records=records, unique_key=['date_id', 'asset_id'])


class FactTechnicalDestination(Destination):
    _COLUMNS = {
        'date_id', 'asset_id', 'portfolio_id',
        'pct_drawdown', 'value_high', 'value_low',
        'ma_20d', 'ma_30d', 'ma_50d',
        'volatility_20d', 'volatility_30d', 'volatility_50d',
        'var_95_1d', 'profit_range_30d',
        'recent_profit_high_30d', 'recent_profit_low_30d',
        'recent_value_high_30d', 'recent_value_low_30d',
    }

    def __init__(self):
        self._repository = RepositoryFactory.get("fact_technical", schema_name="analytics")

    def load(self, data: List[Dict]) -> None:
        records = [{k: v for k, v in r.items() if k in self._COLUMNS} for r in data]
        self._repository.upsert(records=records, unique_key=['date_id', 'asset_id'])


class FactSignalDestination(Destination):
    _COLUMNS = {
        'date_id', 'asset_id', 'portfolio_id',
        'dca_bias', 'ma_crossover_signal',
        'price_above_ma_20d', 'price_above_ma_50d',
    }

    def __init__(self):
        self._repository = RepositoryFactory.get("fact_signal", schema_name="analytics")

    def load(self, data: List[Dict]) -> None:
        records = [{k: v for k, v in r.items() if k in self._COLUMNS} for r in data]
        self._repository.upsert(records=records, unique_key=['date_id', 'asset_id'])


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class PipelineAssetGold(BaseGoldPipeline):
    _pipeline_name = "pipeline_asset_gold"

    def __init__(self):
        self._db = SQLModelClient(DATABASE_URL)
        self._source = AssetGoldSource()
        self._transformation = AssetGoldTransformation()
        self._validator = SchemaValidator(AssetGoldRecord, layer="gold")
        self._dead_letter = DeadLetterDestination()
        self._fact_destinations = [
            FactPriceDestination(),
            FactValuationDestination(),
            FactReturnDestination(),
            FactTechnicalDestination(),
            FactSignalDestination(),
        ]

    def _ensure_dimensions(self):
        """
        Upserts dim_portfolio and dim_asset before the source query runs.
        The source query joins both tables, so they must exist first.

        dim_portfolio: one row — the Trading212 account.
        dim_asset: one row per ticker currently held in staging.asset.
        """
        with self._db as db:
            db.execute("""
                INSERT INTO analytics.dim_portfolio (portfolio_id, name, base_currency)
                VALUES ('trading212', 'Trading212', 'GBP')
                ON CONFLICT (portfolio_id) DO NOTHING
            """)
            db.execute("""
                INSERT INTO analytics.dim_asset (asset_id, ticker, name, asset_type, currency)
                SELECT DISTINCT ON (ticker)
                    id          AS asset_id,
                    ticker,
                    name,
                    'STOCK'     AS asset_type,
                    currency
                FROM staging.asset
                ORDER BY ticker, data_timestamp DESC
                ON CONFLICT (ticker) DO NOTHING
            """)


if __name__ == "__main__":
    PipelineAssetGold().run()
