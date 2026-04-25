from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE
from pipeline.infrastructure.factories.pipeline_factory import PipelineFactory

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_fred_bronze():
    pipeline = PipelineFactory.get("fred_bronze")
    logger.info("Running FRED bronze pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_fred_silver():
    pipeline = PipelineFactory.get("fred_silver")
    logger.info("Running FRED silver pipeline")
    pipeline.run()


@flow
def flow_fred():
    logger.info("Starting FRED ingestion flow")
    task_fred_bronze()
    task_fred_silver()
    logger.info("FRED flow complete")
