import os
import json
import logging
from datetime import timedelta
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from src.services.analytics.query import AssetMetricQuery
from src.services.analytics.funcs import FuncAssetDerivedMetric
from src.services.analytics.sink import SinkAssetMetric
from src.services.analytics.app.processes import CalcAssetMetric

from src.shared.utils.custom_logger import customer_logger


logging = customer_logger("asset_flow_run")

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def calc_metric(query, func, sink):
    x = CalcAssetMetric(query, func, sink)
    x.run()
    
@flow
def trading_212_asset_metric():
    logging.info("Starting the flow to calculate asset metrics")
    logging.info("Starting process")

    query = AssetMetricQuery
    func = FuncAssetDerivedMetric
    sink = SinkAssetMetric
    calc_metric(query, func, sink)

    
cron="1 * * * *"
if __name__ == "__main__":
    trading_212_asset_metric.serve(
        name="trading_212_asset_metric", interval=timedelta(seconds=3600))  # 60min