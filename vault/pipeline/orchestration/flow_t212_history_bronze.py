from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from prefect.logging import loggers

from pipeline.infrastructure.factories.pipeline_factory import PipelineFactory

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_trading212_history_bronze():
    pipeline = PipelineFactory.get("t212_history_bronze")
    logger.info("Running Trading212 history bronze pipeline")
    pipeline.run()


@flow
def flow_t212_history_bronze():
    logger.info("Ingestion Trading212 history events")
    task_trading212_history_bronze()
    logger.info("flow complete")


if __name__ == "__main__":
    flow_t212_history_bronze()
