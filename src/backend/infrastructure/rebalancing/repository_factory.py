from .rebalance_config_repository import PostgresRebalanceConfigRepository
from .rebalance_plan_repository import PostgresRebalancePlanRepository


class RebalancingRepositoryFactory:
    def get_config_repo(self) -> PostgresRebalanceConfigRepository:
        return PostgresRebalanceConfigRepository()

    def get_plan_repo(self) -> PostgresRebalancePlanRepository:
        return PostgresRebalancePlanRepository()
