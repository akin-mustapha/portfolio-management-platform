import os
from dotenv import load_dotenv

from shared.database.client import SQLModelClient
from shared.utils.custom_logger import customer_logger
from shared.notifications.email import EmailClient

from .domain.entities import RebalanceConfig, RebalancePlan
from .infrastructure.repositories.repository_factory import RebalancingRepositoryFactory
from .plan_generator import generate_plan

load_dotenv()

logging = customer_logger("rebalancing_service")

DATABASE_URL = os.getenv("DATABASE_URL")


class RebalancingService:
    def __init__(self):
        logging.info("Initializing RebalancingService")
        self._repo_factory = RebalancingRepositoryFactory()
        self._analytics_client = SQLModelClient(DATABASE_URL)

    def load_configs(self) -> list[RebalanceConfig]:
        """Load all active rebalance configs with tickers from portfolio schema."""
        repo = self._repo_factory.get_config_repo()
        rows = repo.select_all_active_with_ticker()
        return [
            RebalanceConfig(
                id=str(r["id"]) if r["id"] is not None else None,
                asset_id=str(r["asset_id"]),
                ticker=r["ticker"],
                target_weight_pct=float(r["target_weight_pct"]),
                min_weight_pct=float(r["min_weight_pct"]),
                max_weight_pct=float(r["max_weight_pct"]),
                risk_tolerance=int(r["risk_tolerance"]),
                rebalance_threshold_pct=float(r["rebalance_threshold_pct"]),
                correction_days=int(r["correction_days"]),
                momentum_bias=int(r["momentum_bias"]),
                is_active=bool(r["is_active"]),
            )
            for r in rows
        ]

    # TODO - SQL CONCERN BELONGS IN THE REPOSITORY LAYER
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
        with self._analytics_client as client:
            result = client.execute(sql)
            rows = result.fetchall()
        return {r["ticker"]: float(r["position_weight_pct"]) for r in rows}

    def generate_and_save_plan(self) -> RebalancePlan | None:
        """Load state, generate plan, persist, email. Returns None if no drift detected."""
        configs = self.load_configs()
        if not configs:
            logging.info("No active rebalance configs — skipping plan generation")
            return None

        current_weights = self.load_current_weights()
        plan = generate_plan(configs, current_weights)

        if plan is None:
            logging.info("All assets within threshold — no plan generated")
            return None

        repo = self._repo_factory.get_plan_repo()
        repo.insert_plan(plan.to_record())
        logging.info(f"Rebalance plan saved: {plan.plan_json['summary']}")

        try:
            EmailClient().send(
                subject="Rebalancing Plan — " + plan.created_date,
                body_text=_format_plan_email(plan),
            )
            latest = repo.get_latest()
            if latest:
                repo.mark_email_sent(str(latest["id"]))
        except Exception as e:
            logging.error(f"Email failed — plan saved but not emailed: {e}")

        return plan

    def get_latest_plan(self) -> dict | None:
        """Return the most recently created plan row, or None."""
        return self._repo_factory.get_plan_repo().get_latest()

    def upsert_config(self, config: RebalanceConfig) -> None:
        """Create or update a rebalance config for an asset (upsert on asset_id)."""
        repo = self._repo_factory.get_config_repo()
        try:
            repo.upsert(records=[config.to_record()], unique_key=["asset_id"])
            logging.info(f"Upserted rebalance config for asset_id={config.asset_id}")
        except Exception as e:
            logging.error(f"Error upserting rebalance config: {e}")
            raise


def _format_plan_email(plan: RebalancePlan) -> str:
    lines = [
        f"Rebalancing Plan — {plan.created_date}",
        f"Target completion: {plan.target_completion_date}",
        f"",
        plan.plan_json.get("summary", ""),
        f"Total portfolio drift: {plan.plan_json.get('total_drift_pct', 0):.1f}%",
        "",
        "--- Actions ---",
    ]
    for action in plan.plan_json.get("actions", []):
        lines.append(
            f"{action['ticker']:10s}  {action['action'].upper():7s}  "
            f"current {action['current_weight_pct']:.1f}% → target {action['target_weight_pct']:.1f}%  "
            f"(drift {action['drift_pct']:+.1f}%)"
        )
        for step in action.get("daily_steps", []):
            lines.append(f"  {step['date']}  →  {step['target_weight_pct']:.1f}%")
    return "\n".join(lines)
