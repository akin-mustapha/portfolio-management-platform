import logging
from prefect import flow, task
from prefect.logging import loggers
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from backend.ingestion.factories.pipeline_factory import PipelineFactory

logger = loggers.get_logger(__name__)

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_account_bronze_pipeline():
    pipeline = PipelineFactory.get("account_bronze")
    logger.info("Running Pipeline")
    pipeline.run()

@flow
def flow_t212_account_bronze():
    logger.info("Starting the flow to fetch account cash")
    logger.info("Starting data ingestion process")
    task_account_bronze_pipeline()
    logger.info("End data ingestion process")

    
if __name__ == "__main__": 
    flow_t212_account_bronze.serve(
        name="t212_account_bronze", interval=timedelta(seconds=700))  # Runs every 5mins