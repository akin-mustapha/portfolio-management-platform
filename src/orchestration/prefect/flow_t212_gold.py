from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE

from pipelines.factories.pipeline_factory import PipelineFactory

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_gold():
    pipeline = PipelineFactory.get("t212_gold")
    logger.info("Running unified gold pipeline")
    pipeline.run()


@flow
def flow_t212_gold():
    logger.info("Starting gold pipeline")
    task_gold()
    logger.info("Gold pipeline complete")
