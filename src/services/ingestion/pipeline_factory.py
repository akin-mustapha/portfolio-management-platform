from src.services.ingestion.app.policies import Pipeline
from src.services.ingestion.pipelines.bronze_asset_pipeline import BronzeAssetIngestionPipeline
from src.services.ingestion.pipelines. silver_asset_pipeline import SilverAssetPipeline
from src.services.ingestion.pipelines.silver_asset_computed_pipeline import SilverAssetComputedPipeline
from src.services.ingestion.pipelines.portfolio_asset_pipeline import PortfolioAssetPipeline

class PipelineFactory:
  _registry = {
    "bronze_asset": BronzeAssetIngestionPipeline,
    "silver_asset": SilverAssetPipeline,
    "silver_asset_computed": SilverAssetComputedPipeline,
    "portfolio_asset_pipeline": PortfolioAssetPipeline,
  }
  @classmethod
  def get(self, name: str) -> Pipeline:
      return self._registry.get(name.lower())()