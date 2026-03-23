from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE
from backend.ingestion.factories.pipeline_factory import PipelineFactory

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_trading212_bronze():
    pipeline = PipelineFactory.get("t212_bronze")
    logger.info("Running account bronze pipeline")
    pipeline.run()

@flow
def flow_t212_bronze():
    logger.info("Ingestion Trading212 Snapshot")
    task_trading212_bronze()
    logger.info("flow complete")
