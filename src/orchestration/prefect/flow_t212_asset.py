from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE
from backend.ingestion.factories.pipeline_factory import PipelineFactory

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_bronze():
    pipeline = PipelineFactory.get("asset_bronze")
    logger.info("Running asset bronze pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_silver():
    pipeline = PipelineFactory.get("asset_silver")
    logger.info("Running asset silver pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_computed_silver():
    pipeline = PipelineFactory.get("asset_computed_silver")
    logger.info("Running asset computed silver pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_gold():
    pipeline = PipelineFactory.get("asset_gold")
    logger.info("Running asset gold pipeline")
    pipeline.run()


@flow
def flow_t212_asset():
    logger.info("Starting asset flow: bronze → silver → computed silver → gold")
    task_asset_bronze()
    task_asset_silver()
    task_asset_computed_silver()
    task_asset_gold()
    logger.info("Asset flow complete")
