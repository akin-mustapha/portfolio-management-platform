from dotenv import load_dotenv

from shared.utils.custom_logger import customer_logger
from backend.services.rebalancing.service import RebalancingService

load_dotenv()

logging = customer_logger("Rebalancing Service")


def build_rebalancing_service() -> RebalancingService:
    return RebalancingService()
