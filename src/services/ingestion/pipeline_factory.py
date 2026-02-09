from src.services.ingestion.app.policies import Pipeline
from src.services.ingestion.pipelines.ingestion_pipeline import IngestionPipeline
from src.services.ingestion.infra.sources import SourceFactory
from src.services.ingestion.infra.transformations import TransformationFactory
from src.services.ingestion.infra.destinations import DestinationFactory
from src.services.ingestion.infra.sink import SinkFactory

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
  
  @register("trading212FullLoaderAssetPipeline")
  def build_trading212_asset_pipeline() -> Pipeline:
    return IngestionPipeline(
        source=SourceFactory.create("trading212_asset"),
        transformation=TransformationFactory.create("None"),
        destination=DestinationFactory.create("None"),
        sink=SinkFactory.create("trading212_full_loader_asset"),
    )
    
  @register("trading212AssetPipeline")
  def build_trading212_asset_pipeline() -> Pipeline:
    return IngestionPipeline(
        source=SourceFactory.create("trading212_asset"),
        transformation=TransformationFactory.create("trading212_asset"),
        destination=DestinationFactory.create("trading212_asset"),
        sink=SinkFactory.create("trading212_asset"),
    )
  @register("trading212AssetSnapshotPipeline")
  def build_trading212_asset_snapshot_pipeline() -> Pipeline:
    return IngestionPipeline(
        source=SourceFactory.create("trading212_asset_snapshot"),
        transformation=TransformationFactory.create("trading212_asset_snapshot"),
        destination=DestinationFactory.create("trading212_asset_snapshot"),
        sink=SinkFactory.create("trading212_asset_snapshot"),
    )
  @register("trading212PortfolioSnapshotPipeline")
  def build_trading212_portfolio_snapshot_pipeline() -> Pipeline:
    return IngestionPipeline(
        source=SourceFactory.create("trading212_portfolio_snapshot"),
        transformation=TransformationFactory.create("trading212_portfolio_snapshot"),
        destination=DestinationFactory.create("trading212_portfolio_snapshot"),
        sink=SinkFactory.create("trading212_portfolio_snapshot"),
    )