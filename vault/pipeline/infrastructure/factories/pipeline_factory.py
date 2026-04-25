from pipeline.etl.policies import Pipeline

from pipeline.etl.runners.pipeline_asset_portfolio import PipelineAssetPortfolio
from pipeline.etl.runners.portfolio_enrichment_synchronizer import (
    enrichment_sychronization,
)
from pipeline.etl.runners.pipeline_bronze_t212 import PipelineT212Bronze
from pipeline.etl.runners.pipeline_bronze_t212_history import PipelineT212History
from pipeline.etl.runners.pipeline_silver_t212 import PipelineT212Silver
from pipeline.etl.runners.pipeline_gold_t212 import PipelineT212Gold
from pipeline.etl.runners.pipeline_bronze_fred import PipelineFredBronze
from pipeline.etl.runners.pipeline_silver_fred import PipelineFredSilver


class PipelineFactory:
    _registry = {
        "asset_portfolio": PipelineAssetPortfolio,
        "enrichment_sychronization": enrichment_sychronization,
        "t212_bronze": PipelineT212Bronze,
        "t212_history_bronze": PipelineT212History,
        "t212_silver": PipelineT212Silver,
        "t212_gold": PipelineT212Gold,
        "fred_bronze": PipelineFredBronze,
        "fred_silver": PipelineFredSilver,
    }

    @classmethod
    def get(self, name: str) -> Pipeline:
        print(self._registry.get(name))
        return self._registry.get(name.lower())()
