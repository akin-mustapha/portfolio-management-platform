from src.services.analytics.interface import Calc
from src.services.analytics.interface import Func, Sink, Query

from src.services.analytics.query import AssetMetricQuery
from src.services.analytics.funcs import FuncAssetDerivedMetric
from src.services.analytics.sink import SinkAssetMetric


class CalcAssetMetric(Calc):
  def __init__(self, query: Query, derived_func: Func, sink: Sink):
    self._query = query
    self._func = derived_func
    self._sink = sink
    
  def run(self):
    data = self._query.get()
    metric = self._func.run(data)
    self._sink.save(metric)


if __name__ == "__main__":
  x = CalcAssetMetric(AssetMetricQuery
                      , FuncAssetDerivedMetric
                      , SinkAssetMetric)
  x.run()