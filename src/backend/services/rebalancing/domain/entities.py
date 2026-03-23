from dataclasses import dataclass


@dataclass
class RebalanceConfig:
    # NOTE: domain rule — asset_id and ticker are required; id is None until persisted
    # ticker is loaded via JOIN to portfolio.asset — not a column in rebalance_config
    id: str | None
    asset_id: str
    ticker: str
    target_weight_pct: float
    min_weight_pct: float
    max_weight_pct: float
    risk_tolerance: int
    rebalance_threshold_pct: float
    correction_days: int
    momentum_bias: int
    is_active: bool = True

    def to_record(self):
        # excludes id (DB-generated) and ticker (not a column, from JOIN)
        return {
            "asset_id": self.asset_id,
            "target_weight_pct": self.target_weight_pct,
            "min_weight_pct": self.min_weight_pct,
            "max_weight_pct": self.max_weight_pct,
            "risk_tolerance": self.risk_tolerance,
            "rebalance_threshold_pct": self.rebalance_threshold_pct,
            "correction_days": self.correction_days,
            "momentum_bias": self.momentum_bias,
            "is_active": self.is_active,
        }


@dataclass
class RebalancePlan:
    # NOTE: domain rule — plan_json must be a non-empty dict with at least one action
    id: str | None
    created_date: str
    target_completion_date: str
    status: str
    plan_json: dict
    email_sent: bool = False

    def to_record(self):
        return {
            "created_date": self.created_date,
            "target_completion_date": self.target_completion_date,
            "status": self.status,
            "plan_json": self.plan_json,
            "email_sent": self.email_sent,
        }
