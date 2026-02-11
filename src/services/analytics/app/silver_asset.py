from src.services.analytics.app.interfaces import Calc
from src.services.analytics.app.interfaces import Func, Sink, Query
from datetime import datetime, UTC

# Inner Polcies, using relative import
# from ..query import AssetSilverQueryRepo
# from ..funcs import FuncAssetDerivedMetric
# from ..sink import SinkSilverAsset
from ..sink import SinkRepositoryFactory

import yaml
import os


import pandas as pd
class SilverAsset(Calc):
  def __init__(self, query: Query, derived_func: Func, sink: Sink):
    self._query = query
    self._func = derived_func
    self._sink = sink
    
  def run(self):
    bronze_asset_df = self._get_v_bronze()
    self._asset(bronze_asset_df)
    self._asset_decoration()
    
  def _get_v_bronze(self):
    bronze_asset = self._query.get_bronze_asset()
    bronze_asset_df = pd.DataFrame(bronze_asset)
    return bronze_asset_df
  
  
  def _asset(self, df):
    df.rename({
      "ticker": "external_id"
    })
    df = df
    df = df[df["ticker"].notna()]
    asset_df = pd.DataFrame()
    asset_df["external_id"] = df["ticker"]
    asset_df["ticker"] = df["ticker"].apply(lambda x: x.split("_")[0])
    asset_df["name"] = df["instrument_name"]
    asset_df["description"] = df["instrument_name"]
    asset_df["broker"] = "Trading 212"
    asset_df["currency"] = df["instrument_currency"]
    asset_df["local_currency"] = df["wallet_currency"]
    asset_df["share"] = df["quantity"]
    asset_df["price"] = df["current_price"]
    asset_df["avg_price"] = df["average_price_paid"]
    asset_df["value"] = df["current_value"]
    asset_df["cost"] = df["total_cost"]
    asset_df["profit"] = df["unrealized_pnl"]
    asset_df["fx_impact"] = df["fx_impact"]
    asset_df["business_key"] = df["business_key"]
    asset_df["updated_timestamp"] = datetime.now(UTC)
    
    # Using ingested date as marker to sequential ordering of data
    asset_df["data_timestamp"] = df['ingested_timestamp']
    
    
    asset_sink = SinkRepositoryFactory.get('asset')
    asset_sink.save(asset_df)
    
  def _asset_decoration(self):
    computed = self._query.get_asset_computed()
    computed_df = pd.DataFrame(computed)
    
    
    asset_computed_sink = SinkRepositoryFactory.get('asset_computed')
    asset_computed_sink.save(computed_df)
    
  


if __name__ == "__main__":
  
  delta_timestamp_path = "delta_timestamp.yml"
  delta_time = None
  if os.path.exists(delta_timestamp_path):
    # print('a')
    with open("./data/delta_timestamp.yml") as f:
      delta_time = yaml.full_load(f)
  if delta_time is None:
    delta_time = {
      "SilverAsset": datetime.now(UTC)
    }

  
  # x = SilverAsset(AssetSilverQueryRepo
  #                     , FuncAssetDerivedMetric
  #                     , SinkSilverAsset)
  
  # x.run()