"""
PortfolioService unit tests — all repository calls are mocked.
No database connection is required.
"""

import pytest
from unittest.mock import MagicMock, patch

from backend.domain.portfolio.value_objects import Ticker
from backend.domain.portfolio.entities import (
    Asset,
    Tag,
    Category,
    AssetTag,
    Industry,
    Sector,
)
from backend.application.portfolio.service import PortfolioService


@pytest.fixture
def mock_repo_factory():
    factory = MagicMock()
    return factory


@pytest.fixture
def service(mock_repo_factory):
    with patch(
        "backend.application.portfolio.service.RepositoryFactory",
        return_value=mock_repo_factory,
    ):
        svc = PortfolioService()
    svc._repo_factory = mock_repo_factory
    return svc


class TestCreateTag:
    def test_happy_path_upserts_tag(self, service, mock_repo_factory):
        tag_repo = MagicMock()
        mock_repo_factory.get.return_value = tag_repo

        tag = Tag(
            id=None,
            name="Growth",
            description="Growth stocks",
            tag_type_id=1,
            created_timestamp="2026-01-01",
        )
        result = service.create_tag(tag)

        tag_repo.upsert.assert_called_once_with(
            [tag.to_record()], ["name", "tag_type_id"]
        )
        assert result is tag

    def test_raises_when_repo_raises(self, service, mock_repo_factory):
        tag_repo = MagicMock()
        tag_repo.upsert.side_effect = RuntimeError("DB error")
        mock_repo_factory.get.return_value = tag_repo

        tag = Tag(
            id=None,
            name="Growth",
            description="",
            tag_type_id=1,
            created_timestamp="2026-01-01",
        )
        with pytest.raises(RuntimeError, match="DB error"):
            service.create_tag(tag)


class TestTagAsset:
    def test_happy_path_inserts_asset_tag(self, service, mock_repo_factory):
        asset_repo = MagicMock()
        asset_repo.select.return_value = [{"id": 1}]
        tag_repo = MagicMock()
        tag_repo.select.return_value = [{"id": 2}]
        asset_tag_repo = MagicMock()

        def get_repo(name):
            return {"asset": asset_repo, "tag": tag_repo, "asset_tag": asset_tag_repo}[
                name
            ]

        mock_repo_factory.get.side_effect = get_repo

        result = service.tag_asset({"asset_id": 1, "tag_id": 2})

        asset_tag_repo.insert.assert_called_once_with([{"asset_id": 1, "tag_id": 2}])
        assert result == {"asset_id": 1, "tag_id": 2}

    def test_raises_when_asset_not_found(self, service, mock_repo_factory):
        asset_repo = MagicMock()
        asset_repo.select.return_value = []  # asset not found
        tag_repo = MagicMock()

        def get_repo(name):
            return {"asset": asset_repo, "tag": tag_repo, "asset_tag": MagicMock()}[
                name
            ]

        mock_repo_factory.get.side_effect = get_repo

        with pytest.raises(ValueError, match="does not exist"):
            service.tag_asset({"asset_id": 99, "tag_id": 2})

    def test_raises_when_tag_not_found(self, service, mock_repo_factory):
        asset_repo = MagicMock()
        asset_repo.select.return_value = [{"id": 1}]
        tag_repo = MagicMock()
        tag_repo.select.return_value = []  # tag not found

        def get_repo(name):
            return {"asset": asset_repo, "tag": tag_repo, "asset_tag": MagicMock()}[
                name
            ]

        mock_repo_factory.get.side_effect = get_repo

        with pytest.raises(ValueError, match="does not exist"):
            service.tag_asset({"asset_id": 1, "tag_id": 99})


class TestRemoveTagFromAsset:
    def test_happy_path_deletes_asset_tag(self, service, mock_repo_factory):
        asset_tag_repo = MagicMock()
        mock_repo_factory.get.return_value = asset_tag_repo

        item_tag = AssetTag(asset_id=1, tag_id=2, created_timestamp=None)
        service.remove_tag_from_asset(item_tag)

        asset_tag_repo.delete.assert_called_once_with({"asset_id": 1, "tag_id": 2})

    def test_raises_when_repo_raises(self, service, mock_repo_factory):
        asset_tag_repo = MagicMock()
        asset_tag_repo.delete.side_effect = RuntimeError("constraint error")
        mock_repo_factory.get.return_value = asset_tag_repo

        with pytest.raises(RuntimeError, match="constraint error"):
            service.remove_tag_from_asset(
                AssetTag(asset_id=1, tag_id=2, created_timestamp=None)
            )


class TestAssignIndustryToSector:
    def test_happy_path_updates_sector(self, service, mock_repo_factory):
        sector_repo = MagicMock()
        sector_repo.select.return_value = [{"id": 3}]
        industry_repo = MagicMock()
        industry_repo.select.return_value = [{"id": 1}]

        def get_repo(name):
            return {"sector": sector_repo, "industry": industry_repo}[name]

        mock_repo_factory.get.side_effect = get_repo

        service.assign_industry_to_sector(sector_id=3, industry_id=1)

        sector_repo.update.assert_called_once_with(
            params={"id": 3}, data={"industry_id": 1}
        )

    def test_raises_when_industry_not_found(self, service, mock_repo_factory):
        sector_repo = MagicMock()
        industry_repo = MagicMock()
        industry_repo.select.return_value = []

        def get_repo(name):
            return {"sector": sector_repo, "industry": industry_repo}[name]

        mock_repo_factory.get.side_effect = get_repo

        with pytest.raises(ValueError, match="Industry with ID"):
            service.assign_industry_to_sector(sector_id=3, industry_id=99)

    def test_raises_when_sector_not_found(self, service, mock_repo_factory):
        sector_repo = MagicMock()
        sector_repo.select.return_value = []
        industry_repo = MagicMock()
        industry_repo.select.return_value = [{"id": 1}]

        def get_repo(name):
            return {"sector": sector_repo, "industry": industry_repo}[name]

        mock_repo_factory.get.side_effect = get_repo

        with pytest.raises(ValueError, match="Sector with ID"):
            service.assign_industry_to_sector(sector_id=99, industry_id=1)


class TestSearchAssetByTag:
    def test_happy_path_returns_assets(self, service, mock_repo_factory):
        asset_tag_repo = MagicMock()
        asset_tag_repo.select_all_by.return_value = [{"asset_id": 1}, {"asset_id": 2}]
        mock_repo_factory.get.return_value = asset_tag_repo

        tag = Tag(
            id=7,
            name="Growth",
            description="",
            tag_type_id=1,
            created_timestamp="2026-01-01",
        )
        result = service.search_asset_by_tag(tag)

        asset_tag_repo.select_all_by.assert_called_once_with({"tag_id": 7})
        assert len(result) == 2

    def test_raises_when_tag_has_no_id(self, service, mock_repo_factory):
        tag = Tag(
            id=None,
            name="Growth",
            description="",
            tag_type_id=1,
            created_timestamp="2026-01-01",
        )

        with pytest.raises(ValueError, match="Tag must have an id"):
            service.search_asset_by_tag(tag)


class TestSearchTagByAsset:
    def test_happy_path_returns_tags(self, service, mock_repo_factory):
        asset_tag_repo = MagicMock()
        asset_tag_repo.select_all_by.return_value = [{"tag_id": 1}]
        mock_repo_factory.get.return_value = asset_tag_repo

        asset = Asset(
            id="asset-1",
            ticker=Ticker("AAPL"),
            name="Apple",
            broker=None,
            currency=None,
        )
        result = service.search_tag_by_asset(asset)

        asset_tag_repo.select_all_by.assert_called_once_with({"asset_id": "asset-1"})
        assert len(result) == 1

    def test_raises_when_asset_has_no_id(self, service, mock_repo_factory):
        asset = Asset(
            id=None, ticker=Ticker("AAPL"), name="Apple", broker=None, currency=None
        )

        with pytest.raises(ValueError, match="Asset must have an id"):
            service.search_tag_by_asset(asset)


class TestSearchTagByAssetId:
    def test_happy_path_returns_tags(self, service, mock_repo_factory):
        asset_tag_repo = MagicMock()
        asset_tag_repo.select_all_by.return_value = [{"tag_id": 3}]
        mock_repo_factory.get.return_value = asset_tag_repo

        result = service.search_tag_by_asset_id("asset-42")

        asset_tag_repo.select_all_by.assert_called_once_with({"asset_id": "asset-42"})
        assert result == [{"tag_id": 3}]

    def test_raises_when_asset_id_is_empty(self, service, mock_repo_factory):
        with pytest.raises(ValueError, match="asset_id is required"):
            service.search_tag_by_asset_id("")


class TestGetAssetByTicker:
    def test_happy_path_returns_asset(self, service, mock_repo_factory):
        asset_repo = MagicMock()
        asset_repo.select.return_value = {"id": "1", "ticker": "AAPL"}
        mock_repo_factory.get.return_value = asset_repo

        result = service.get_asset_by_ticker(
            "AAPL", broker="Trading212", currency="USD"
        )

        asset_repo.select.assert_called_once_with(
            {"ticker": "AAPL", "broker": "Trading212", "currency": "USD"}
        )
        assert result["ticker"] == "AAPL"

    def test_returns_none_when_ticker_is_empty(self, service, mock_repo_factory):
        result = service.get_asset_by_ticker("")

        mock_repo_factory.get.assert_not_called()
        assert result is None


class TestGetAllMethods:
    @pytest.mark.parametrize(
        "method,repo_key",
        [
            ("get_all_tags", "tag"),
            ("get_all_industries", "industry"),
            ("get_all_sectors", "sector"),
            ("get_all_categories", "category"),
        ],
    )
    def test_happy_path_delegates_to_repo(
        self, service, mock_repo_factory, method, repo_key
    ):
        repo = MagicMock()
        repo.select_all.return_value = [{"id": 1}]
        mock_repo_factory.get.return_value = repo

        result = getattr(service, method)()

        mock_repo_factory.get.assert_called_with(repo_key)
        assert result == [{"id": 1}]

    def test_get_all_tags_raises_when_repo_raises(self, service, mock_repo_factory):
        repo = MagicMock()
        repo.select_all.side_effect = RuntimeError("connection lost")
        mock_repo_factory.get.return_value = repo

        with pytest.raises(RuntimeError, match="connection lost"):
            service.get_all_tags()


class TestCreateIndustry:
    def test_happy_path_upserts_industry(self, service, mock_repo_factory):
        industry_repo = MagicMock()
        mock_repo_factory.get.return_value = industry_repo

        industry = Industry(
            id=None,
            name="Technology",
            description="Tech",
            created_timestamp="2026-01-01",
        )
        service.create_industry(industry)

        industry_repo.upsert.assert_called_once_with(
            records=[industry.to_record()], unique_key=["name"]
        )

    def test_raises_when_repo_raises(self, service, mock_repo_factory):
        industry_repo = MagicMock()
        industry_repo.upsert.side_effect = RuntimeError("unique violation")
        mock_repo_factory.get.return_value = industry_repo

        industry = Industry(
            id=None, name="Technology", description="", created_timestamp="2026-01-01"
        )
        with pytest.raises(RuntimeError, match="unique violation"):
            service.create_industry(industry)


class TestCreateSector:
    def test_happy_path_upserts_sector(self, service, mock_repo_factory):
        sector_repo = MagicMock()
        mock_repo_factory.get.return_value = sector_repo

        sector = Sector(
            id=None,
            industry_id=1,
            name="Software",
            description="SW",
            created_timestamp="2026-01-01",
        )
        service.create_sector(sector)

        sector_repo.upsert.assert_called_once_with(
            records=[sector.to_record()], unique_key=["name"]
        )

    def test_raises_when_repo_raises(self, service, mock_repo_factory):
        sector_repo = MagicMock()
        sector_repo.upsert.side_effect = RuntimeError("DB error")
        mock_repo_factory.get.return_value = sector_repo

        sector = Sector(
            id=None,
            industry_id=1,
            name="Software",
            description="",
            created_timestamp="2026-01-01",
        )
        with pytest.raises(RuntimeError, match="DB error"):
            service.create_sector(sector)


class TestCreateCategory:
    def test_happy_path_upserts_category(self, service, mock_repo_factory):
        category_repo = MagicMock()
        mock_repo_factory.get.return_value = category_repo

        category = Category(
            id=None,
            name="Equity",
            description="Equities",
            created_timestamp="2026-01-01",
        )
        service.create_category(category)

        category_repo.upsert.assert_called_once_with(
            records=[category.to_record()], unique_key=["name"]
        )

    def test_raises_when_repo_raises(self, service, mock_repo_factory):
        category_repo = MagicMock()
        category_repo.upsert.side_effect = RuntimeError("DB error")
        mock_repo_factory.get.return_value = category_repo

        category = Category(
            id=None, name="Equity", description="", created_timestamp="2026-01-01"
        )
        with pytest.raises(RuntimeError, match="DB error"):
            service.create_category(category)
