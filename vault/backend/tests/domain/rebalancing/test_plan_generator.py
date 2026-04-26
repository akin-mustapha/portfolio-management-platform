"""
Tests for generate_plan — a pure function with no DB access.
All cases can be driven by constructing domain objects directly.
"""

from datetime import date, timedelta

from backend.domain.rebalancing.entities import RebalanceConfig
from backend.domain.rebalancing.plan_generator import generate_plan
from backend.domain.rebalancing.value_objects import RebalanceThreshold, WeightBand


def _config(
    ticker: str,
    target: float,
    threshold: float,
    correction_days: int = 5,
    is_active: bool = True,
) -> RebalanceConfig:
    return RebalanceConfig(
        id=None,
        asset_id="asset-1",
        ticker=ticker,
        weight_band=WeightBand(target=target, min=max(0.0, target - 10), max=min(100.0, target + 10)),
        rebalance_threshold=RebalanceThreshold(threshold),
        correction_days=correction_days,
        is_active=is_active,
    )


class TestGeneratePlan:
    def test_returns_plan_when_drift_exceeds_threshold(self):
        configs = [_config("AAPL", target=10.0, threshold=2.0)]
        current_weights = {"AAPL": 15.0}  # drift = 5.0 > threshold 2.0

        plan = generate_plan(configs, current_weights)

        assert plan is not None
        assert len(plan.plan_json["actions"]) == 1
        action = plan.plan_json["actions"][0]
        assert action["ticker"] == "AAPL"
        assert action["action"] == "reduce"
        assert action["drift_pct"] == 5.0

    def test_returns_none_when_all_within_threshold(self):
        configs = [_config("AAPL", target=10.0, threshold=2.0)]
        current_weights = {"AAPL": 10.5}  # drift = 0.5 <= threshold 2.0

        plan = generate_plan(configs, current_weights)

        assert plan is None

    def test_returns_none_for_empty_configs(self):
        plan = generate_plan([], {"AAPL": 15.0})

        assert plan is None

    def test_inactive_config_is_skipped(self):
        configs = [_config("AAPL", target=10.0, threshold=2.0, is_active=False)]
        current_weights = {"AAPL": 50.0}  # massive drift but config is inactive

        plan = generate_plan(configs, current_weights)

        assert plan is None

    def test_missing_ticker_in_weights_defaults_to_zero(self):
        configs = [_config("TSLA", target=10.0, threshold=2.0)]
        current_weights = {}  # TSLA not present — defaults to 0.0, drift = -10.0

        plan = generate_plan(configs, current_weights)

        assert plan is not None
        assert plan.plan_json["actions"][0]["action"] == "increase"

    def test_plan_has_correct_daily_steps_count(self):
        configs = [_config("AAPL", target=10.0, threshold=2.0, correction_days=3)]
        current_weights = {"AAPL": 15.0}

        plan = generate_plan(configs, current_weights)

        action = plan.plan_json["actions"][0]
        assert len(action["daily_steps"]) == 3

    def test_plan_completion_date_matches_max_correction_days(self):
        configs = [
            _config("AAPL", target=10.0, threshold=2.0, correction_days=3),
            _config("MSFT", target=20.0, threshold=2.0, correction_days=7),
        ]
        current_weights = {"AAPL": 15.0, "MSFT": 28.0}

        plan = generate_plan(configs, current_weights)

        expected = (date.today() + timedelta(days=7)).isoformat()
        assert plan.target_completion_date == expected

    def test_plan_status_is_draft(self):
        configs = [_config("AAPL", target=10.0, threshold=2.0)]
        current_weights = {"AAPL": 20.0}

        plan = generate_plan(configs, current_weights)

        assert str(plan.status) == "draft"

    def test_total_drift_sums_absolute_drifts(self):
        configs = [
            _config("AAPL", target=10.0, threshold=2.0),  # drift +5
            _config("MSFT", target=20.0, threshold=2.0),  # drift -5
        ]
        current_weights = {"AAPL": 15.0, "MSFT": 15.0}

        plan = generate_plan(configs, current_weights)

        assert plan.plan_json["total_drift_pct"] == 10.0

    def test_config_with_zero_correction_days_is_skipped(self):
        configs = [_config("AAPL", target=10.0, threshold=2.0, correction_days=0)]
        current_weights = {"AAPL": 50.0}

        plan = generate_plan(configs, current_weights)

        assert plan is None
