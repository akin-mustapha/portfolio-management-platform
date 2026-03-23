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
        """All current assets LEFT JOIN rebalance_config.
        Assets with no config row get default values via COALESCE.
        portfolio.asset is SCD2 — to_timestamp IS NULL identifies current records.
        """
        sql = """
            SELECT
                a.id                                          AS asset_id,
                a.ticker,
                rc.id,
                COALESCE(rc.target_weight_pct,       0.0)    AS target_weight_pct,
                COALESCE(rc.min_weight_pct,          0.0)    AS min_weight_pct,
                COALESCE(rc.max_weight_pct,          100.0)  AS max_weight_pct,
                COALESCE(rc.risk_tolerance,          50)     AS risk_tolerance,
                COALESCE(rc.rebalance_threshold_pct, 2.0)    AS rebalance_threshold_pct,
                COALESCE(rc.correction_days,         3)      AS correction_days,
                COALESCE(rc.momentum_bias,           0)      AS momentum_bias,
                COALESCE(rc.is_active,               TRUE)   AS is_active
            FROM portfolio.asset a
            LEFT JOIN portfolio.rebalance_config rc ON rc.asset_id = a.id
            WHERE a.to_timestamp IS NULL
            ORDER BY a.ticker
        """
        with self._client as client:
            result = client.execute(sql)
            rows = result.fetchall()
        return [dict(r._mapping) for r in rows]
