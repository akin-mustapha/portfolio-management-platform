from src.services.ingestion_service.application.interfaces import Pipeline
from src.services.ingestion_service.application.pipelines import Trading212IngestionPipeline
from src.services.ingestion_service.application.sources import Trading212AssetSource, Trading212AssetSnapshotSource, Trading212PortfolioSnapshotSource
from src.services.ingestion_service.application.trasformations import Trading212AssetTransformation, Trading212AssetSnapshotTransformation, Trading212PortfolioSnapshotTransformation
from src.services.ingestion_service.application.destinations import Trading212AssetDestination, Trading212AssetSnapshotDestination, Trading212PortfolioSnapshotDestination
from src.services.ingestion_service.application.sink import Trading212AssetSink, Trading212AssetSnapshotSink, Trading212PortfolioSnapshotSink

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
    return Trading212IngestionPipeline(
        source=Trading212AssetSource(),
        transformation=Trading212AssetTransformation(),
        destination=Trading212AssetDestination(),
        sink=Trading212AssetSink(),
    )
  @register("trading212AssetSnapshotPipeline")
  def build_trading212_asset_snapshot_pipeline() -> Pipeline:
    return Trading212IngestionPipeline(
        source=Trading212AssetSnapshotSource(),
        transformation=Trading212AssetSnapshotTransformation(),
        destination=Trading212AssetSnapshotDestination(),
        sink=Trading212AssetSnapshotSink(),
    )
  @register("trading212PortfolioSnapshotPipeline")
  def build_trading212_portfolio_snapshot_pipeline() -> Pipeline:
    return Trading212IngestionPipeline(
        source=Trading212PortfolioSnapshotSource(),
        transformation=Trading212PortfolioSnapshotTransformation(),
        destination=Trading212PortfolioSnapshotDestination(),
        sink=Trading212PortfolioSnapshotSink(),
    )