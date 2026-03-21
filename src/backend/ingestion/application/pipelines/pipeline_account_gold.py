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
from ...domain.schemas.gold.account_gold import AccountGoldRecord

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

class AccountGoldSource(Source):
    """
    Pulls the latest account snapshot and joins staging.account_computed for
    computed metrics. Aggregates fx_impact across all positions. Requires
    dim_portfolio to be seeded first (handled by PipelineAccountGold._ensure_dimensions).
    """

    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)

    def extract(self):
        sql = """
            WITH cte_fx AS (
            SELECT data_timestamp::DATE, SUM(fx_impact) AS fx_impact_total
            FROM staging.asset sa
            GROUP BY data_timestamp::DATE
            )
            , cte_account AS (
            SELECT
                ROW_NUMBER()OVER(PARTITION BY data_timestamp::DATE ORDER BY data_timestamp DESC) AS rn
                , *
            FROM staging.account
            ORDER BY data_timestamp DESC
            )
            SELECT
                TO_CHAR(a.data_timestamp, 'YYYYMMDD')::INTEGER          AS date_id,
                dp.id                                               AS portfolio_id,

                a.total_value,
                a.investments_total_cost                             AS total_cost,
                a.investments_unrealized_pnl                         AS unrealized_pnl,
                a.investments_unrealized_pnl
                    / NULLIF(a.investments_total_cost, 0) * 100      AS unrealized_pnl_pct,
                a.investments_realized_pnl                           AS realized_pnl,

                c.daily_change_abs,
                c.daily_change_pct,

                a.cash_available_to_trade                            AS cash_available,
                a.cash_reserved_for_orders                           AS cash_reserved,
                a.cash_in_pies,
                c.cash_deployment_ratio,

                fx.fx_impact_total,
                c.portfolio_volatility_weighted

            FROM cte_account a
            JOIN staging.account_computed c
                ON c.account_id = a.id
            CROSS JOIN (
                SELECT id
                FROM analytics.dim_portfolio
                WHERE portfolio_id = 'trading212'
            ) dp
            LEFT JOIN cte_fx fx
            ON fx.data_timestamp = a.data_timestamp::DATE
            WHERE a.rn = 1
        """
        with self._client as db:
            result = db.execute(sql)
        return result.fetchall()


# ---------------------------------------------------------------------------
# Transformation
# ---------------------------------------------------------------------------

class AccountGoldTransformation(Transformation):
    """
    Converts SQLAlchemy Row objects to plain dicts.
    All computation is already done in staging.account_computed.
    """

    def transform(self, data: list) -> list[Dict]:
        return [dict(row._mapping) for row in data]


# ---------------------------------------------------------------------------
# Destination
# ---------------------------------------------------------------------------

class FactPortfolioDailyDestination(Destination):
    _COLUMNS = {
        'date_id', 'portfolio_id',
        'total_value', 'total_cost', 'unrealized_pnl', 'unrealized_pnl_pct',
        'realized_pnl', 'daily_change_abs', 'daily_change_pct',
        'cash_available', 'cash_reserved', 'cash_in_pies', 'cash_deployment_ratio',
        'fx_impact_total', 'portfolio_volatility_weighted',
    }

    def __init__(self):
        self._repository = RepositoryFactory.get("fact_portfolio_daily", schema_name="analytics")

    def load(self, data: List[Dict]) -> None:
        records = [{k: v for k, v in r.items() if k in self._COLUMNS} for r in data]
        self._repository.upsert(records=records, unique_key=['date_id', 'portfolio_id'])


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class PipelineAccountGold(BaseGoldPipeline):
    _pipeline_name = "pipeline_account_gold"

    def __init__(self):
        self._db = SQLModelClient(DATABASE_URL)
        self._source = AccountGoldSource()
        self._transformation = AccountGoldTransformation()
        self._validator = SchemaValidator(AccountGoldRecord, layer="gold")
        self._dead_letter = DeadLetterDestination()
        self._fact_destinations = [
            FactPortfolioDailyDestination(),
        ]

    def _ensure_dimensions(self):
        with self._db as db:
            db.execute("""
                INSERT INTO analytics.dim_portfolio (portfolio_id, name, base_currency)
                VALUES ('trading212', 'Trading212', 'GBP')
                ON CONFLICT (portfolio_id) DO NOTHING
            """)


if __name__ == "__main__":
    PipelineAccountGold().run()
