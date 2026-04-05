from dataclasses import dataclass

from .value_objects import WeightBand, RebalanceThreshold, PlanStatus


@dataclass
class RebalanceConfig:
    # NOTE: domain rule — asset_id and ticker are required; id is None until persisted
    # ticker is loaded via JOIN to portfolio.asset — not a column in rebalance_config
    id: str | None
    asset_id: str
    ticker: str
    weight_band: WeightBand
    rebalance_threshold: RebalanceThreshold
    correction_days: int
    is_active: bool = True

    @property
    def target_weight_pct(self) -> float:
        return self.weight_band.target

    @property
    def min_weight_pct(self) -> float:
        return self.weight_band.min

    @property
    def max_weight_pct(self) -> float:
        return self.weight_band.max

    @property
    def rebalance_threshold_pct(self) -> float:
        return self.rebalance_threshold.value

    def to_record(self):
        # excludes id (DB-generated) and ticker (not a column, from JOIN)
        return {
            "asset_id": self.asset_id,
            "target_weight_pct": self.weight_band.target,
            "min_weight_pct": self.weight_band.min,
            "max_weight_pct": self.weight_band.max,
            "rebalance_threshold_pct": self.rebalance_threshold.value,
            "correction_days": self.correction_days,
            "is_active": self.is_active,
        }


@dataclass
class RebalancePlan:
    # NOTE: domain rule — plan_json must be a non-empty dict with at least one action
    id: str | None
    created_date: str
    target_completion_date: str
    status: PlanStatus
    plan_json: dict
    email_sent: bool = False

    def to_record(self):
        return {
            "created_date": self.created_date,
            "target_completion_date": self.target_completion_date,
            "status": str(self.status),
            "plan_json": self.plan_json,
            "email_sent": self.email_sent,
        }
