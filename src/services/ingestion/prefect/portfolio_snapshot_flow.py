import logging
from prefect import flow, task
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from src.services.ingestion.app.pipelines. pipeline_factory import PipelineFactory

from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("portfolio_snapshot_flow_run")

@task(retry_delay_seconds=30, retries=2, cache_policy=NO_CACHE)
def ingest_portfolio_snapshot():
    pipeline = PipelineFactory.get("trading212PortfolioSnapshotPipeline")
    pipeline.run()

@flow
def trading_212_portfolio_snapshot():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    ingest_portfolio_snapshot()
    logging.info("End data ingestion process")

    
if __name__ == "__main__": 
    # trading_212_portfolio_snapshot.serve(
    #     name="trading_212_portfolio_snapshot", interval=timedelta(seconds=3600))  # Runs every 5mins

    pipeline = PipelineFactory.get("trading212PortfolioSnapshotPipeline")
    pipeline.run()