from backend.application.rebalancing.service import RebalancingService


def build_rebalancing_service() -> RebalancingService:
    return RebalancingService()
