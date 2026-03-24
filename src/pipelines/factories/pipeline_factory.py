from ..application.policies import Pipeline

from ..application.runners.pipeline_asset_bronze import PipelineAssetBronze
from ..application.runners.pipeline_asset_silver import PipelineAssetSilver
from ..application.runners.pipeline_asset_portfolio import PipelineAssetPortfolio
from ..application.runners.pipeline_account_bronze import PipelineAccountBronze
from ..application.runners.pipeline_account_silver import PipelineAccountSilver
from ..application.runners.pipeline_asset_computed_silver import PipelineAssetComputedSilver
from ..application.runners.pipeline_account_computed_silver import PipelineAccountComputedSilver
from ..application.runners.portfolio_enrichment_synchronizer import enrichment_sychronization

class PipelineFactory:
  _registry = {
    "asset_bronze": PipelineAssetBronze,
    "asset_silver": PipelineAssetSilver,
    "asset_computed_silver": PipelineAssetComputedSilver,
    "asset_portfolio": PipelineAssetPortfolio,
    "account_bronze": PipelineAccountBronze,
    "account_silver": PipelineAccountSilver,
    "account_computed_silver": PipelineAccountComputedSilver,
    "enrichment_sychronization": enrichment_sychronization,
  }
  @classmethod
  def get(self, name: str) -> Pipeline:
    print(self._registry.get(name))
    return self._registry.get(name.lower())()