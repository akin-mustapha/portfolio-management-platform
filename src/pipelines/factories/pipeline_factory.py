from ..application.policies import Pipeline

from ..application.runners.pipeline_asset_bronze import PipelineAssetBronze
from ..application.runners.pipeline_asset_silver import PipelineAssetSilver
from ..application.runners.pipeline_asset_portfolio import PipelineAssetPortfolio
from ..application.runners.pipeline_account_bronze import PipelineAccountBronze
from ..application.runners.pipeline_account_silver import PipelineAccountSilver
from ..application.runners.pipeline_asset_computed_silver import (
    PipelineAssetComputedSilver,
)
from ..application.runners.pipeline_account_computed_silver import (
    PipelineAccountComputedSilver,
)
from ..application.runners.portfolio_enrichment_synchronizer import (
    enrichment_sychronization,
)
from ..application.runners.pipeline_bronze_t212 import PipelineT212Bronze
from ..application.runners.pipeline_silver_t212 import PipelineT212Silver
from ..application.runners.pipeline_gold_t212 import PipelineT212Gold
from ..application.runners.pipeline_bronze_fred import PipelineFredBronze
from ..application.runners.pipeline_silver_fred import PipelineFredSilver


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
        "t212_bronze": PipelineT212Bronze,
        "t212_silver": PipelineT212Silver,
        "t212_gold": PipelineT212Gold,
        "fred_bronze": PipelineFredBronze,
        "fred_silver": PipelineFredSilver,
    }

    @classmethod
    def get(self, name: str) -> Pipeline:
        print(self._registry.get(name))
        return self._registry.get(name.lower())()
