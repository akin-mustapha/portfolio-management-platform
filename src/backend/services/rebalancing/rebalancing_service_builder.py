from backend.services.rebalancing.service import RebalancingService


def build_rebalancing_service() -> RebalancingService:
    return RebalancingService()
