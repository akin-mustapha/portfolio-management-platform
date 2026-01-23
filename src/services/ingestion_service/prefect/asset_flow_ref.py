from src.services.ingestion_service.application.pipelines. pipeline_factory import PipelineFactory

if __name__ == "__main__":
  pipeline = PipelineFactory.get("trading212AssetPipeline")
  pipeline.run()