from backend.application.rebalancing.service import RebalancingService
from backend.infrastructure.rebalancing.rebalance_config_repository import (
    PostgresRebalanceConfigRepository,
)
from backend.infrastructure.rebalancing.rebalance_plan_repository import (
    PostgresRebalancePlanRepository,
)


def build_rebalancing_service() -> RebalancingService:
    return RebalancingService(
        config_repo=PostgresRebalanceConfigRepository(),
        plan_repo=PostgresRebalancePlanRepository(),
    )
