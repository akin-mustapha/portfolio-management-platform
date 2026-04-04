"""
RebalancingService unit tests — all repository calls are mocked.
No database connection is required.
"""
import pytest
from unittest.mock import MagicMock, patch

from backend.domain.rebalancing.entities import RebalanceConfig, RebalancePlan
from backend.domain.rebalancing.value_objects import WeightBand, RebalanceThreshold, PlanStatus
from backend.application.rebalancing.service import RebalancingService


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
def mock_factory():
    factory = MagicMock()
    return factory


@pytest.fixture
def service(mock_factory):
    with patch(
        "backend.application.rebalancing.service.RebalancingRepositoryFactory",
        return_value=mock_factory,
    ):
        svc = RebalancingService()
    svc._repo_factory = mock_factory
    return svc


class TestLoadConfigs:
    def test_happy_path_maps_rows_to_domain_objects(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.select_all_active_with_ticker.return_value = [_RAW_CONFIG_ROW]
        mock_factory.get_config_repo.return_value = config_repo

        configs = service.load_configs()

        assert len(configs) == 1
        cfg = configs[0]
        assert isinstance(cfg, RebalanceConfig)
        assert cfg.ticker == "AAPL"
        assert cfg.target_weight_pct == 10.0
        assert cfg.rebalance_threshold_pct == 2.0

    def test_returns_empty_list_when_no_rows(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.select_all_active_with_ticker.return_value = []
        mock_factory.get_config_repo.return_value = config_repo

        configs = service.load_configs()

        assert configs == []

    def test_raises_when_repo_raises(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.select_all_active_with_ticker.side_effect = RuntimeError("DB down")
        mock_factory.get_config_repo.return_value = config_repo

        with pytest.raises(RuntimeError, match="DB down"):
            service.load_configs()


class TestGenerateAndSavePlan:
    def test_happy_path_saves_and_returns_plan(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.select_all_active_with_ticker.return_value = [_RAW_CONFIG_ROW]

        plan_repo = MagicMock()
        plan_repo.load_current_weights.return_value = {"AAPL": 20.0}  # drift = 10 > threshold 2
        plan_repo.get_latest.return_value = {"id": "plan-1"}

        mock_factory.get_config_repo.return_value = config_repo
        mock_factory.get_plan_repo.return_value = plan_repo

        with patch("backend.application.rebalancing.service.EmailClient") as MockEmail:
            MockEmail.return_value.send.return_value = None
            result = service.generate_and_save_plan()

        assert result is not None
        assert isinstance(result, RebalancePlan)
        plan_repo.insert_plan.assert_called_once()

    def test_returns_none_when_no_configs(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.select_all_active_with_ticker.return_value = []
        mock_factory.get_config_repo.return_value = config_repo

        result = service.generate_and_save_plan()

        assert result is None

    def test_returns_none_when_all_within_threshold(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.select_all_active_with_ticker.return_value = [_RAW_CONFIG_ROW]

        plan_repo = MagicMock()
        plan_repo.load_current_weights.return_value = {"AAPL": 10.5}  # drift 0.5 < threshold 2.0

        mock_factory.get_config_repo.return_value = config_repo
        mock_factory.get_plan_repo.return_value = plan_repo

        result = service.generate_and_save_plan()

        assert result is None
        plan_repo.insert_plan.assert_not_called()

    def test_plan_saved_even_when_email_fails(self, service, mock_factory):
        import smtplib

        config_repo = MagicMock()
        config_repo.select_all_active_with_ticker.return_value = [_RAW_CONFIG_ROW]

        plan_repo = MagicMock()
        plan_repo.load_current_weights.return_value = {"AAPL": 20.0}
        plan_repo.get_latest.return_value = {"id": "plan-1"}

        mock_factory.get_config_repo.return_value = config_repo
        mock_factory.get_plan_repo.return_value = plan_repo

        with patch("backend.application.rebalancing.service.EmailClient") as MockEmail:
            MockEmail.return_value.send.side_effect = smtplib.SMTPException("SMTP error")
            result = service.generate_and_save_plan()

        # Plan must be saved even when email fails
        plan_repo.insert_plan.assert_called_once()
        assert result is not None


class TestGetLatestPlan:
    def test_happy_path_returns_plan_dict(self, service, mock_factory):
        plan_repo = MagicMock()
        plan_repo.get_latest.return_value = {"id": "plan-1", "status": "draft"}
        mock_factory.get_plan_repo.return_value = plan_repo

        result = service.get_latest_plan()

        assert result == {"id": "plan-1", "status": "draft"}

    def test_returns_none_when_no_plan_exists(self, service, mock_factory):
        plan_repo = MagicMock()
        plan_repo.get_latest.return_value = None
        mock_factory.get_plan_repo.return_value = plan_repo

        result = service.get_latest_plan()

        assert result is None


class TestGetAssetIdByTicker:
    def test_happy_path_returns_asset_id(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.get_asset_id_by_ticker.return_value = "asset-42"
        mock_factory.get_config_repo.return_value = config_repo

        result = service.get_asset_id_by_ticker("AAPL")

        config_repo.get_asset_id_by_ticker.assert_called_once_with("AAPL")
        assert result == "asset-42"

    def test_returns_none_when_ticker_not_found(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.get_asset_id_by_ticker.return_value = None
        mock_factory.get_config_repo.return_value = config_repo

        result = service.get_asset_id_by_ticker("UNKNOWN")

        assert result is None


class TestUpsertConfig:
    def test_happy_path_calls_upsert_on_asset_id(self, service, mock_factory):
        config_repo = MagicMock()
        mock_factory.get_config_repo.return_value = config_repo

        config = RebalanceConfig(
            id=None,
            asset_id="asset-1",
            ticker="AAPL",
            weight_band=WeightBand(target=10.0, min=5.0, max=15.0),
            rebalance_threshold=RebalanceThreshold(2.0),
            correction_days=7,
        )
        service.upsert_config(config)

        config_repo.upsert.assert_called_once_with(
            records=[config.to_record()], unique_key=["asset_id"]
        )

    def test_raises_when_repo_raises(self, service, mock_factory):
        config_repo = MagicMock()
        config_repo.upsert.side_effect = RuntimeError("DB write error")
        mock_factory.get_config_repo.return_value = config_repo

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
