import os
from dotenv import load_dotenv

from shared.repositories.base_table_repository import BaseTableRepository
from shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class PostgresRebalanceConfigRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "asset_id": "asset_id",
            "target_weight_pct": "target_weight_pct",
            "min_weight_pct": "min_weight_pct",
            "max_weight_pct": "max_weight_pct",
            "risk_tolerance": "risk_tolerance",
            "rebalance_threshold_pct": "rebalance_threshold_pct",
            "correction_days": "correction_days",
            "momentum_bias": "momentum_bias",
            "is_active": "is_active",
        }
        super().__init__("rebalance_config", schema_name="portfolio", field_map=field_map)

    def select_all_active_with_ticker(self) -> list[dict]:
        """Load all active configs joined with portfolio.asset to get ticker.
        portfolio.asset is SCD2 — to_timestamp IS NULL identifies current records.
        """
        sql = """
            SELECT
                rc.id,
                rc.asset_id,
                a.ticker,
                rc.target_weight_pct,
                rc.min_weight_pct,
                rc.max_weight_pct,
                rc.risk_tolerance,
                rc.rebalance_threshold_pct,
                rc.correction_days,
                rc.momentum_bias,
                rc.is_active
            FROM portfolio.rebalance_config rc
            JOIN portfolio.asset a
                ON a.id = rc.asset_id
               AND a.to_timestamp IS NULL
            WHERE rc.is_active = TRUE
        """
        with self._client as client:
            result = client.execute(sql)
            rows = result.fetchall()
        return [dict(r._mapping) for r in rows]
