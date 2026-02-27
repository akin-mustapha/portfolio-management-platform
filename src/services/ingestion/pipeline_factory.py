from .app.policies import Pipeline

from .pipelines.pipeline_asset_bronze import PipelineAssetBronze
from .pipelines.pipeline_asset_silver import PipelineAssetSilver
from .pipelines.pipeline_asset_portfolio import PipelineAssetPortfolio
from .pipelines.pipeline_account_bronze import PipelineAccountBronze
from .pipelines.pipeline_account_silver import PipelineAccountSilver
from .pipelines.pipeline_asset_computed_silver import PipelineAssetComputedSilver

class PipelineFactory:
  _registry = {
    "asset_bronze": PipelineAssetBronze,
    "asset_silver": PipelineAssetSilver,
    "asset_computed_silver": PipelineAssetComputedSilver,
    "asset_portfolio": PipelineAssetPortfolio,
    "account_bronze": PipelineAccountBronze,
    "account_silver": PipelineAccountSilver,
  }
  @classmethod
  def get(self, name: str) -> Pipeline:
      return self._registry.get(name.lower())()