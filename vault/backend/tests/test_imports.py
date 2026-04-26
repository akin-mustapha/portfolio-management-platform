"""
Smoke tests — verify every module in the new DDD layout is importable.
These catch missing __init__.py files, typos in module paths, and circular imports
before any logic is exercised.
"""


class TestDomainPortfolioImports:
    def test_value_objects_importable(self):
        from backend.domain.portfolio.value_objects import Broker, Currency, Ticker

        assert Ticker is not None
        assert Currency is not None
        assert Broker is not None

    def test_entities_importable(self):
        from backend.domain.portfolio.entities import (
            Asset,
            AssetTag,
            Category,
            Industry,
            Sector,
            Tag,
        )

        assert Asset is not None
        assert Tag is not None
        assert Category is not None
        assert AssetTag is not None
        assert Industry is not None
        assert Sector is not None

    def test_interfaces_importable(self):
        from backend.domain.portfolio.interfaces import AssetQueryRepository

        assert AssetQueryRepository is not None


class TestDomainRebalancingImports:
    def test_value_objects_importable(self):
        from backend.domain.rebalancing.value_objects import (
            PlanStatus,
            RebalanceThreshold,
            WeightBand,
        )

        assert WeightBand is not None
        assert RebalanceThreshold is not None
        assert PlanStatus is not None

    def test_entities_importable(self):
        from backend.domain.rebalancing.entities import (
            RebalanceConfig,
            RebalancePlan,
        )

        assert RebalanceConfig is not None
        assert RebalancePlan is not None


class TestApplicationPortfolioImports:
    def test_service_importable(self):
        from backend.application.portfolio.service import PortfolioService

        assert PortfolioService is not None

    def test_factory_importable(self):
        from backend.application.portfolio.factory import build_portfolio_service

        assert build_portfolio_service is not None


class TestApplicationRebalancingImports:
    def test_service_importable(self):
        from backend.application.rebalancing.service import RebalancingService

        assert RebalancingService is not None

    def test_factory_importable(self):
        from backend.application.rebalancing.factory import build_rebalancing_service

        assert build_rebalancing_service is not None

    def test_plan_generator_importable(self):
        from backend.application.rebalancing.plan_generator import generate_plan

        assert generate_plan is not None


class TestInfrastructurePortfolioImports:
    def test_repository_factory_importable(self):
        from backend.infrastructure.portfolio.repository_factory import (
            RepositoryFactory,
        )

        assert RepositoryFactory is not None

    def test_asset_repository_importable(self):
        from backend.infrastructure.portfolio.asset_repository import (
            PostgresAssetRepository,
            SQLiteAssetRepository,
        )

        assert PostgresAssetRepository is not None
        assert SQLiteAssetRepository is not None

    def test_tag_repository_importable(self):
        from backend.infrastructure.portfolio.tag_repository import (
            PostgresTagRepository,
            SQLiteTagRepository,
        )

        assert PostgresTagRepository is not None
        assert SQLiteTagRepository is not None

    def test_category_repository_importable(self):
        from backend.infrastructure.portfolio.category_repository import (
            PostgresCategoryRepository,
            SQLiteCategoryRepository,
        )

        assert PostgresCategoryRepository is not None
        assert SQLiteCategoryRepository is not None

    def test_industry_repository_importable(self):
        from backend.infrastructure.portfolio.industry_repository import (
            PostgresIndustryRepository,
            SQLiteIndustryRepository,
        )

        assert PostgresIndustryRepository is not None
        assert SQLiteIndustryRepository is not None

    def test_sector_repository_importable(self):
        from backend.infrastructure.portfolio.sector_repository import (
            PostgresSectorRepository,
            SQLiteSectorRepository,
        )

        assert PostgresSectorRepository is not None
        assert SQLiteSectorRepository is not None

    def test_asset_tag_repository_importable(self):
        from backend.infrastructure.portfolio.asset_tag_repository import (
            PostgresAssetTagRepository,
            SQLiteAssetTagRepository,
        )

        assert PostgresAssetTagRepository is not None
        assert SQLiteAssetTagRepository is not None


class TestInfrastructureRebalancingImports:
    def test_repository_factory_importable(self):
        from backend.infrastructure.rebalancing.repository_factory import (
            RebalancingRepositoryFactory,
        )

        assert RebalancingRepositoryFactory is not None

    def test_config_repository_importable(self):
        from backend.infrastructure.rebalancing.rebalance_config_repository import (
            PostgresRebalanceConfigRepository,
        )

        assert PostgresRebalanceConfigRepository is not None

    def test_plan_repository_importable(self):
        from backend.infrastructure.rebalancing.rebalance_plan_repository import (
            PostgresRebalancePlanRepository,
        )

        assert PostgresRebalancePlanRepository is not None


class TestInfrastructureCredentialsImports:
    def test_credentials_repository_importable(self):
        from backend.infrastructure.credentials.repository import (
            CredentialsRepository,
        )

        assert CredentialsRepository is not None
