import pytest

from v2.backend.domain.rebalancing.value_objects import (
    WeightBand,
    RebalanceThreshold,
    PlanStatus,
)


class TestWeightBand:
    def test_valid_weight_band(self):
        wb = WeightBand(target=10.0, min=5.0, max=15.0)
        assert wb.target == 10.0
        assert wb.min == 5.0
        assert wb.max == 15.0

    def test_target_below_min_raises(self):
        with pytest.raises(ValueError, match="invariant violated"):
            WeightBand(target=3.0, min=5.0, max=15.0)

    def test_target_above_max_raises(self):
        with pytest.raises(ValueError, match="invariant violated"):
            WeightBand(target=20.0, min=5.0, max=15.0)

    def test_value_above_100_raises(self):
        with pytest.raises(ValueError, match=r"\[0\.0, 100\.0\]"):
            WeightBand(target=101.0, min=5.0, max=110.0)

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match=r"\[0\.0, 100\.0\]"):
            WeightBand(target=-1.0, min=-5.0, max=15.0)

    def test_weight_band_equality(self):
        assert WeightBand(10.0, 5.0, 15.0) == WeightBand(10.0, 5.0, 15.0)

    def test_weight_band_is_immutable(self):
        wb = WeightBand(10.0, 5.0, 15.0)
        with pytest.raises((AttributeError, TypeError)):
            wb.target = 20.0

    def test_boundary_values_are_valid(self):
        # min == target == max is a valid degenerate band
        wb = WeightBand(target=10.0, min=10.0, max=10.0)
        assert wb.target == wb.min == wb.max


class TestRebalanceThreshold:
    def test_valid_threshold(self):
        rt = RebalanceThreshold(2.0)
        assert rt.value == 2.0

    def test_zero_threshold_raises(self):
        with pytest.raises(ValueError, match=r"> 0\.0"):
            RebalanceThreshold(0.0)

    def test_negative_threshold_raises(self):
        with pytest.raises(ValueError, match=r"> 0\.0"):
            RebalanceThreshold(-1.5)

    def test_threshold_equality(self):
        assert RebalanceThreshold(2.0) == RebalanceThreshold(2.0)


class TestPlanStatus:
    def test_valid_status_pending(self):
        ps = PlanStatus("pending")
        assert str(ps) == "pending"

    def test_valid_status_active(self):
        assert str(PlanStatus("active")) == "active"

    def test_valid_status_completed(self):
        assert str(PlanStatus("completed")) == "completed"

    def test_valid_status_cancelled(self):
        assert str(PlanStatus("cancelled")) == "cancelled"

    def test_valid_status_draft(self):
        assert str(PlanStatus("draft")) == "draft"

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="PlanStatus must be one of"):
            PlanStatus("unknown")

    def test_uppercase_status_raises(self):
        # Values are case-sensitive — "PENDING" is not valid
        with pytest.raises(ValueError, match="PlanStatus must be one of"):
            PlanStatus("PENDING")

    def test_status_equality(self):
        assert PlanStatus("pending") == PlanStatus("pending")
