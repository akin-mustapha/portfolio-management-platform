from src.services.ingestion_service.application.interfaces.pipeline import Pipeline
from inspect import isclass, ismodule

from src.services.ingestion_service.application.pipelines import Trading212AssetPipeline

from src.services.ingestion_service.application.sources.trading_212_asset_source import Trading212AssetSource
from src.services.ingestion_service.application.transformation.trading212_asset_trasformation import Trading212AssetTransformation
from src.services.ingestion_service.application.destination.trading212_asset_destination import Trading212AssetDestination


PIPELINE_REGISTRY = {}

def register(name: str):
    def decorator(builder):
        PIPELINE_REGISTRY[name] = builder
        return builder
    return decorator

class PipelineFactory:
  @staticmethod
  def get(name: str) -> Pipeline:
      return PIPELINE_REGISTRY[name]()
    
  @register("trading212AssetPipeline")
  def build_trading212_pipeline() -> Pipeline:
    return Trading212AssetPipeline(
        source=Trading212AssetSource(),
        transformation=Trading212AssetTransformation(),
        destination=Trading212AssetDestination(),
    )