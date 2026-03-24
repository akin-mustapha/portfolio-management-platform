import json
import os
from dotenv import load_dotenv

from shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class PostgresRebalancePlanRepository:
    """Custom repository for rebalance_plan — bypasses BaseTableRepository
    to handle the JSONB plan_json column with an explicit ::jsonb cast.
    """

    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)

    def insert_plan(self, record: dict) -> None:
        sql = """
            INSERT INTO portfolio.rebalance_plan
                (created_date, target_completion_date, status, plan_json, email_sent)
            VALUES
                (:created_date, :target_completion_date, :status, CAST(:plan_json AS jsonb), :email_sent)
        """
        params = {
            "created_date": record["created_date"],
            "target_completion_date": record["target_completion_date"],
            "status": record["status"],
            "plan_json": (
                json.dumps(record["plan_json"])
                if isinstance(record["plan_json"], dict)
                else record["plan_json"]
            ),
            "email_sent": record["email_sent"],
        }
        with self._client as client:
            client.execute(sql, params)

    def mark_email_sent(self, plan_id: str) -> None:
        sql = """
            UPDATE portfolio.rebalance_plan
            SET email_sent = TRUE, updated_timestamp = now()
            WHERE id = :id
        """
        with self._client as client:
            client.execute(sql, {"id": plan_id})

    def load_current_weights(self) -> dict[str, float]:
        """Return {ticker: position_weight_pct} from the latest gold layer snapshot."""
        sql = """
            WITH latest AS (
                SELECT asset_id, MAX(date_id) AS max_date_id
                FROM analytics.fact_valuation
                GROUP BY asset_id
            )
            SELECT da.ticker, COALESCE(fv.position_weight_pct, 0.0) AS position_weight_pct
            FROM analytics.fact_valuation fv
            JOIN latest
                ON fv.asset_id = latest.asset_id
               AND fv.date_id  = latest.max_date_id
            JOIN analytics.dim_asset da ON da.asset_id = fv.asset_id
        """
        with self._client as client:
            result = client.execute(sql)
            rows = result.fetchall()
        return {
            r._mapping["ticker"]: float(r._mapping["position_weight_pct"]) for r in rows
        }

    def get_latest(self) -> dict | None:
        sql = """
            SELECT id, created_date, target_completion_date, status, plan_json, email_sent
            FROM portfolio.rebalance_plan
            ORDER BY created_timestamp DESC
            LIMIT 1
        """
        with self._client as client:
            result = client.execute(sql)
            row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)
