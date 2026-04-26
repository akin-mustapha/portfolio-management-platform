import pytest
from v2.backend.domain.rebalancing.entities import RebalanceConfig, RebalancePlan
from v2.backend.domain.rebalancing.value_objects import (
    PlanStatus,
    RebalanceThreshold,
    WeightBand,
)


class TestRebalanceConfigToRecord:
    @pytest.fixture
    def config(self):
        return RebalanceConfig(
            id="abc-123",
            asset_id="asset-1",
            ticker="AAPL",
            weight_band=WeightBand(target=10.0, min=5.0, max=15.0),
            rebalance_threshold=RebalanceThreshold(2.0),
            correction_days=7,
            is_active=True,
        )

    def test_to_record_unpacks_weight_band(self, config):
        record = config.to_record()

        assert record["target_weight_pct"] == 10.0
        assert record["min_weight_pct"] == 5.0
        assert record["max_weight_pct"] == 15.0

    def test_to_record_unpacks_threshold(self, config):
        record = config.to_record()

        assert record["rebalance_threshold_pct"] == 2.0

    def test_to_record_excludes_id_and_ticker(self, config):
        record = config.to_record()

        assert "id" not in record
        assert "ticker" not in record

    def test_property_accessors_delegate_to_value_objects(self, config):
        assert config.target_weight_pct == 10.0
        assert config.min_weight_pct == 5.0
        assert config.max_weight_pct == 15.0
        assert config.rebalance_threshold_pct == 2.0

    def test_invalid_weight_band_raises_on_construction(self):
        with pytest.raises(ValueError):
            RebalanceConfig(
                id=None,
                asset_id="asset-1",
                ticker="AAPL",
                weight_band=WeightBand(target=20.0, min=5.0, max=15.0),  # target > max
                rebalance_threshold=RebalanceThreshold(2.0),
                correction_days=7,
            )


class TestRebalancePlanToRecord:
    @pytest.fixture
    def plan(self):
        return RebalancePlan(
            id=None,
            created_date="2026-04-04",
            target_completion_date="2026-04-11",
            status=PlanStatus("draft"),
            plan_json={"summary": "1 asset outside threshold", "actions": []},
            email_sent=False,
        )

    def test_to_record_serialises_status_as_string(self, plan):
        record = plan.to_record()

        assert record["status"] == "draft"
        assert isinstance(record["status"], str)

    def test_to_record_excludes_id(self, plan):
        record = plan.to_record()

        assert "id" not in record

    def test_to_record_preserves_plan_json(self, plan):
        record = plan.to_record()

        assert record["plan_json"]["summary"] == "1 asset outside threshold"

    def test_to_record_with_invalid_status_raises(self):
        with pytest.raises(ValueError, match="PlanStatus must be one of"):
            RebalancePlan(
                id=None,
                created_date="2026-04-04",
                target_completion_date="2026-04-11",
                status=PlanStatus("invalid"),
                plan_json={},
            )
