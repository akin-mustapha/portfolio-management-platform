from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE
from backend.ingestion.factories.pipeline_factory import PipelineFactory

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_account_silver():
    pipeline = PipelineFactory.get("account_silver")
    logger.info("Running account silver pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_account_computed_silver():
    pipeline = PipelineFactory.get("account_computed_silver")
    logger.info("Running account computed silver pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_account_gold():
    pipeline = PipelineFactory.get("account_gold")
    logger.info("Running account gold pipeline")
    pipeline.run()


@flow
def flow_t212_account():
    logger.info("Starting account flow: silver → computed silver → gold")
    task_account_silver()
    task_account_computed_silver()
    task_account_gold()
    logger.info("Account flow complete")
