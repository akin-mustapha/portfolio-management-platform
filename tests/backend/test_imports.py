"""
Smoke tests — verify every module in the new DDD layout is importable.
These catch missing __init__.py files, typos in module paths, and circular imports
before any logic is exercised.
"""


class TestDomainPortfolioImports:
    def test_value_objects_importable(self):
        from backend.domain.portfolio.value_objects import Ticker, Currency, Broker

        assert Ticker
        assert Currency
        assert Broker

    def test_entities_importable(self):
        from backend.domain.portfolio.entities import (
            Asset,
            Tag,
            Category,
            AssetTag,
            Industry,
            Sector,
        )

        assert Asset
        assert Tag
        assert Category
        assert AssetTag
        assert Industry
        assert Sector

    def test_interfaces_importable(self):
        from backend.domain.portfolio.interfaces import AssetQueryRepository

        assert AssetQueryRepository


class TestDomainRebalancingImports:
    def test_value_objects_importable(self):
        from backend.domain.rebalancing.value_objects import (
            WeightBand,
            RebalanceThreshold,
            PlanStatus,
        )

        assert WeightBand
        assert RebalanceThreshold
        assert PlanStatus

    def test_entities_importable(self):
        from backend.domain.rebalancing.entities import RebalanceConfig, RebalancePlan

        assert RebalanceConfig
        assert RebalancePlan


class TestApplicationPortfolioImports:
    def test_service_importable(self):
        from backend.application.portfolio.service import PortfolioService

        assert PortfolioService

    def test_factory_importable(self):
        from backend.application.portfolio.factory import build_portfolio_service

        assert build_portfolio_service


class TestApplicationRebalancingImports:
    def test_service_importable(self):
        from backend.application.rebalancing.service import RebalancingService

        assert RebalancingService

    def test_factory_importable(self):
        from backend.application.rebalancing.factory import build_rebalancing_service

        assert build_rebalancing_service

    def test_plan_generator_importable(self):
        from backend.application.rebalancing.plan_generator import generate_plan

        assert generate_plan


class TestInfrastructurePortfolioImports:
    def test_repository_factory_importable(self):
        from backend.infrastructure.portfolio.repository_factory import (
            RepositoryFactory,
        )

        assert RepositoryFactory

    def test_asset_repository_importable(self):
        from backend.infrastructure.portfolio.asset_repository import (
            PostgresAssetRepository,
            SQLiteAssetRepository,
        )

        assert PostgresAssetRepository
        assert SQLiteAssetRepository

    def test_tag_repository_importable(self):
        from backend.infrastructure.portfolio.tag_repository import (
            PostgresTagRepository,
            SQLiteTagRepository,
        )

        assert PostgresTagRepository
        assert SQLiteTagRepository

    def test_category_repository_importable(self):
        from backend.infrastructure.portfolio.category_repository import (
            PostgresCategoryRepository,
            SQLiteCategoryRepository,
        )

        assert PostgresCategoryRepository
        assert SQLiteCategoryRepository

    def test_industry_repository_importable(self):
        from backend.infrastructure.portfolio.industry_repository import (
            PostgresIndustryRepository,
            SQLiteIndustryRepository,
        )

        assert PostgresIndustryRepository
        assert SQLiteIndustryRepository

    def test_sector_repository_importable(self):
        from backend.infrastructure.portfolio.sector_repository import (
            PostgresSectorRepository,
            SQLiteSectorRepository,
        )

        assert PostgresSectorRepository
        assert SQLiteSectorRepository

    def test_asset_tag_repository_importable(self):
        from backend.infrastructure.portfolio.asset_tag_repository import (
            PostgresAssetTagRepository,
            SQLiteAssetTagRepository,
        )

        assert PostgresAssetTagRepository
        assert SQLiteAssetTagRepository


class TestInfrastructureRebalancingImports:
    def test_repository_factory_importable(self):
        from backend.infrastructure.rebalancing.repository_factory import (
            RebalancingRepositoryFactory,
        )

        assert RebalancingRepositoryFactory

    def test_config_repository_importable(self):
        from backend.infrastructure.rebalancing.rebalance_config_repository import (
            PostgresRebalanceConfigRepository,
        )

        assert PostgresRebalanceConfigRepository

    def test_plan_repository_importable(self):
        from backend.infrastructure.rebalancing.rebalance_plan_repository import (
            PostgresRebalancePlanRepository,
        )

        assert PostgresRebalancePlanRepository


class TestInfrastructureCredentialsImports:
    def test_credentials_repository_importable(self):
        from backend.infrastructure.credentials.repository import CredentialsRepository

        assert CredentialsRepository
