from prefect import flow, task
from prefect.cache_policies import NO_CACHE

from pipeline.etl.runners.portfolio_enrichment_synchronizer import (
    enrichment_sychronization,
)

from shared.utils.custom_logger import customer_logger

logging = customer_logger("enrichment_flow")


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_enrichment_sychronization():
    enrichment_sychronization()


@flow
def flow_t212_enrichment_sychronization():
    logging.info("Starting the Data Enrichment Synchronization")
    task_enrichment_sychronization()
    logging.info("End process")
