from src.app.interfaces.analytics import Calc
from src.app.interfaces.analytics import Func, Sink, Query

# Inner Polcies, using relative import
from .query import AssetMetricQuery
from .funcs import FuncAssetDerivedMetric
from .sink import SinkAssetMetric


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