from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE

from backend.services.rebalancing.rebalancing_service_builder import build_rebalancing_service

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_generate_rebalance_plan():
    service = build_rebalancing_service()
    logger.info("Generating rebalance plan")
    plan = service.generate_and_save_plan()
    if plan:
        logger.info(f"Plan saved: {plan.plan_json['summary']}")
    else:
        logger.info("No plan generated — all assets within threshold")


@flow
def flow_rebalance_plan():
    logger.info("Starting rebalance plan flow")
    task_generate_rebalance_plan()
    logger.info("Rebalance plan flow complete")
