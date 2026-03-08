---
name: Services
description: Existing services.
---

# Services

## Event Consumer

```sh
  python3 -m src.services.event_consumer.main
```

## Event Producer

```python
from src.services.ingestion.pipeline_factory import PipelineFactory

if __name__ == "__main__":

  """
  trading212AssetEventProducer
  """
  event = EventProducerFactory.get("trading212AssetEventProducer")
  event.run()

```

## Ingestion

```python
from src.services.ingestion.pipeline_factory import PipelineFactory

if __name__ == "__main__":

  """
  trading212AssetPipeline
  trading212AssetSnapshotPipeline
  trading212PortfolioSnapshotPipeline
  """
  pipeline = PipePipelineFactory.get("trading212AssetPipeline")
  pipeline.run()


```
