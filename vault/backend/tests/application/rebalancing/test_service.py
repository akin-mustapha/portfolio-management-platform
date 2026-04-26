"""
RebalancingService unit tests — all repository calls are mocked.
No database connection is required.
"""

from unittest.mock import MagicMock, patch

import pytest

from backend.application.rebalancing.service import RebalancingService
from backend.domain.rebalancing.entities import RebalanceConfig, RebalancePlan
from backend.domain.rebalancing.value_objects import RebalanceThreshold, WeightBand

_RAW_CONFIG_ROW = {
    "id": "cfg-1",
    "asset_id": "asset-1",
    "ticker": "AAPL",
    "target_weight_pct": 10.0,
    "min_weight_pct": 5.0,
    "max_weight_pct": 15.0,
    "rebalance_threshold_pct": 2.0,
    "correction_days": 7,
    "is_active": True,
}


@pytest.fixture
def mock_config_repo():
    return MagicMock()


@pytest.fixture
def mock_plan_repo():
    return MagicMock()


@pytest.fixture
def service(mock_config_repo, mock_plan_repo):
    return RebalancingService(
        config_repo=mock_config_repo,
        plan_repo=mock_plan_repo,
    )


class TestLoadConfigs:
    def test_happy_path_maps_rows_to_domain_objects(self, service, mock_config_repo):
        mock_config_repo.select_all_active_with_ticker.return_value = [_RAW_CONFIG_ROW]

        configs = service.load_configs()

        assert len(configs) == 1
        cfg = configs[0]
        assert isinstance(cfg, RebalanceConfig)
        assert cfg.ticker == "AAPL"
        assert cfg.target_weight_pct == 10.0
        assert cfg.rebalance_threshold_pct == 2.0

    def test_returns_empty_list_when_no_rows(self, service, mock_config_repo):
        mock_config_repo.select_all_active_with_ticker.return_value = []

        configs = service.load_configs()

        assert configs == []

    def test_raises_when_repo_raises(self, service, mock_config_repo):
        mock_config_repo.select_all_active_with_ticker.side_effect = RuntimeError("DB down")

        with pytest.raises(RuntimeError, match="DB down"):
            service.load_configs()


class TestGenerateAndSavePlan:
    def test_happy_path_saves_and_returns_plan(self, service, mock_config_repo, mock_plan_repo):
        mock_config_repo.select_all_active_with_ticker.return_value = [_RAW_CONFIG_ROW]
        mock_plan_repo.load_current_weights.return_value = {"AAPL": 20.0}  # drift = 10 > threshold 2
        mock_plan_repo.get_latest.return_value = {"id": "plan-1"}

        with patch("backend.application.rebalancing.service.EmailClient") as MockEmail:
            MockEmail.return_value.send.return_value = None
            result = service.generate_and_save_plan()

        assert result is not None
        assert isinstance(result, RebalancePlan)
        mock_plan_repo.insert_plan.assert_called_once()

    def test_returns_none_when_no_configs(self, service, mock_config_repo):
        mock_config_repo.select_all_active_with_ticker.return_value = []

        result = service.generate_and_save_plan()

        assert result is None

    def test_returns_none_when_all_within_threshold(self, service, mock_config_repo, mock_plan_repo):
        mock_config_repo.select_all_active_with_ticker.return_value = [_RAW_CONFIG_ROW]
        mock_plan_repo.load_current_weights.return_value = {"AAPL": 10.5}  # drift 0.5 < threshold 2.0

        result = service.generate_and_save_plan()

        assert result is None
        mock_plan_repo.insert_plan.assert_not_called()

    def test_plan_saved_even_when_email_fails(self, service, mock_config_repo, mock_plan_repo):
        import smtplib

        mock_config_repo.select_all_active_with_ticker.return_value = [_RAW_CONFIG_ROW]
        mock_plan_repo.load_current_weights.return_value = {"AAPL": 20.0}
        mock_plan_repo.get_latest.return_value = {"id": "plan-1"}

        with patch("backend.application.rebalancing.service.EmailClient") as MockEmail:
            MockEmail.return_value.send.side_effect = smtplib.SMTPException("SMTP error")
            result = service.generate_and_save_plan()

        # Plan must be saved even when email fails
        mock_plan_repo.insert_plan.assert_called_once()
        assert result is not None


class TestGetLatestPlan:
    def test_happy_path_returns_plan_dict(self, service, mock_plan_repo):
        mock_plan_repo.get_latest.return_value = {"id": "plan-1", "status": "draft"}

        result = service.get_latest_plan()

        assert result == {"id": "plan-1", "status": "draft"}

    def test_returns_none_when_no_plan_exists(self, service, mock_plan_repo):
        mock_plan_repo.get_latest.return_value = None

        result = service.get_latest_plan()

        assert result is None


class TestGetAssetIdByTicker:
    def test_happy_path_returns_asset_id(self, service, mock_config_repo):
        mock_config_repo.get_asset_id_by_ticker.return_value = "asset-42"

        result = service.get_asset_id_by_ticker("AAPL")

        mock_config_repo.get_asset_id_by_ticker.assert_called_once_with("AAPL")
        assert result == "asset-42"

    def test_returns_none_when_ticker_not_found(self, service, mock_config_repo):
        mock_config_repo.get_asset_id_by_ticker.return_value = None

        result = service.get_asset_id_by_ticker("UNKNOWN")

        assert result is None


class TestUpsertConfig:
    def test_happy_path_calls_upsert_on_asset_id(self, service, mock_config_repo):
        config = RebalanceConfig(
            id=None,
            asset_id="asset-1",
            ticker="AAPL",
            weight_band=WeightBand(target=10.0, min=5.0, max=15.0),
            rebalance_threshold=RebalanceThreshold(2.0),
            correction_days=7,
        )
        service.upsert_config(config)

        mock_config_repo.upsert.assert_called_once_with(records=[config.to_record()], unique_key=["asset_id"])

    def test_raises_when_repo_raises(self, service, mock_config_repo):
        mock_config_repo.upsert.side_effect = RuntimeError("DB write error")

        config = RebalanceConfig(
            id=None,
            asset_id="asset-1",
            ticker="AAPL",
            weight_band=WeightBand(target=10.0, min=5.0, max=15.0),
            rebalance_threshold=RebalanceThreshold(2.0),
            correction_days=7,
        )
        with pytest.raises(RuntimeError, match="DB write error"):
            service.upsert_config(config)
