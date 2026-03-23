from ..application.policies import Pipeline

from ..application.pipelines.pipeline_asset_bronze import PipelineAssetBronze
from ..application.pipelines.pipeline_asset_silver import PipelineAssetSilver
from ..application.pipelines.pipeline_asset_portfolio import PipelineAssetPortfolio
from ..application.pipelines.pipeline_account_bronze import PipelineAccountBronze
from ..application.pipelines.pipeline_account_silver import PipelineAccountSilver
from ..application.pipelines.pipeline_asset_computed_silver import PipelineAssetComputedSilver
from ..application.pipelines.pipeline_account_computed_silver import PipelineAccountComputedSilver
from ..application.pipelines.pipeline_asset_gold import PipelineAssetGold
from ..application.pipelines.pipeline_account_gold import PipelineAccountGold
from ..application.pipelines.pipeline_bronze_t212 import PipelineT212Bronze
from ..application.pipelines.portfolio_enrichment_synchronizer import enrichment_sychronization

class PipelineFactory:
  _registry = {
    "asset_bronze": PipelineAssetBronze,
    "asset_silver": PipelineAssetSilver,
    "asset_computed_silver": PipelineAssetComputedSilver,
    "asset_gold": PipelineAssetGold,
    "asset_portfolio": PipelineAssetPortfolio,
    "account_bronze": PipelineAccountBronze,
    "account_silver": PipelineAccountSilver,
    "account_computed_silver": PipelineAccountComputedSilver,
    "account_gold": PipelineAccountGold,
    "enrichment_sychronization": enrichment_sychronization,
    "t212_bronze": PipelineT212Bronze,
  }
  @classmethod
  def get(self, name: str) -> Pipeline:
    return self._registry.get(name.lower())()