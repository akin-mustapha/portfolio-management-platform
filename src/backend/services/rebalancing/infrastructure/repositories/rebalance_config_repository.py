import os
from dotenv import load_dotenv

from shared.repositories.base_table_repository import BaseTableRepository
from shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_DEFAULT_TARGET_WEIGHT_PCT = 0.0
_DEFAULT_MIN_WEIGHT_PCT = 0.0
_DEFAULT_MAX_WEIGHT_PCT = 100.0
_DEFAULT_THRESHOLD_PCT = 2.0
_DEFAULT_CORRECTION_DAYS = 7
_DEFAULT_IS_ACTIVE = True


class PostgresRebalanceConfigRepository(BaseTableRepository):
    def __init__(self):
        field_map = {
            "asset_id": "asset_id",
            "target_weight_pct": "target_weight_pct",
            "min_weight_pct": "min_weight_pct",
            "max_weight_pct": "max_weight_pct",
            "rebalance_threshold_pct": "rebalance_threshold_pct",
            "correction_days": "correction_days",
            "is_active": "is_active",
        }
        super().__init__(
            "rebalance_config", schema_name="portfolio", field_map=field_map
        )

    def get_asset_id_by_ticker(self, ticker: str) -> str | None:
        """Return the asset_id for a ticker (most recently created record)."""
        sql = """
            SELECT id AS asset_id
            FROM portfolio.asset
            WHERE ticker = :ticker
            ORDER BY updated_timestamp DESC NULLS LAST
            LIMIT 1
        """
        with self._client as client:
            result = client.execute(sql, {"ticker": ticker})
            row = result.fetchone()
        return str(row._mapping["asset_id"]) if row else None

    def select_all_active_with_ticker(self) -> list[dict]:
        """All assets LEFT JOIN rebalance_config, one row per ticker (most recent asset record).
        Assets with no config row get default values via COALESCE.
        """
        sql = """
            SELECT DISTINCT ON (a.ticker)
                a.id                                          AS asset_id,
                a.ticker,
                rc.id,
                COALESCE(rc.target_weight_pct,       :default_target)    AS target_weight_pct,
                COALESCE(rc.min_weight_pct,          :default_min)       AS min_weight_pct,
                COALESCE(rc.max_weight_pct,          :default_max)       AS max_weight_pct,
                COALESCE(rc.rebalance_threshold_pct, :default_threshold) AS rebalance_threshold_pct,
                COALESCE(rc.correction_days,         :default_days)      AS correction_days,
                COALESCE(rc.is_active,               :default_active)    AS is_active
            FROM portfolio.asset a
            LEFT JOIN portfolio.rebalance_config rc ON rc.asset_id = a.id
            ORDER BY a.ticker, a.updated_timestamp DESC NULLS LAST
        """
        params = {
            "default_target": _DEFAULT_TARGET_WEIGHT_PCT,
            "default_min": _DEFAULT_MIN_WEIGHT_PCT,
            "default_max": _DEFAULT_MAX_WEIGHT_PCT,
            "default_threshold": _DEFAULT_THRESHOLD_PCT,
            "default_days": _DEFAULT_CORRECTION_DAYS,
            "default_active": _DEFAULT_IS_ACTIVE,
        }
        with self._client as client:
            result = client.execute(sql, params)
            rows = result.fetchall()
        return [dict(r._mapping) for r in rows]
