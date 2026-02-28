import logging
from prefect import flow, task
from datetime import timedelta
from ingestion.pipeline_factory import PipelineFactory
from prefect.cache_policies import NO_CACHE

from shared.utils.custom_logger import customer_logger

logging = customer_logger("asset_flow_run")

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_account_silver_pipeline():
    pipeline = PipelineFactory.get("account_silver")
    pipeline.run()


# @task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
# def task_asset_computed_silver():
#     pipeline = PipelineFactory.get("asset_computed_silver")
#     pipeline.run()

@flow
def flow_t212_account_silver():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    task_account_silver_pipeline()
    # task_asset_computed_silver()
    logging.info("End data ingestion process")

    
if __name__ == "__main__": 
    flow_t212_account_silver.serve(
        name="t212_account_silver", interval=timedelta(seconds=800))  # Runs every 5mins