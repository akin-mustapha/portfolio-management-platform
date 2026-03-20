from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE
from backend.ingestion.factories.pipeline_factory import PipelineFactory

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_account_bronze():
    pipeline = PipelineFactory.get("account_bronze")
    logger.info("Running account bronze pipeline")
    pipeline.run()


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


@flow
def flow_t212_account():
    logger.info("Starting account flow: bronze → silver → computed silver")
    task_account_bronze()
    task_account_silver()
    task_account_computed_silver()
    logger.info("Account flow complete")
