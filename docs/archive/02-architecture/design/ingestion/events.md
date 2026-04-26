---
name: Event
---

# Events

## Event Consumer

```sh
  python3 -m pipelines.infrastructure.kafka.consumer_main
```

## Event Producer

```python
from pipelines.factories.event_producer_factory import EventProducerFactory

if __name__ == "__main__":

  """
  trading212AssetEventProducer
  """
  event = EventProducerFactory.get("trading212AssetEventProducer")
  event.run()

```

## Ingestion

```python
from pipelines.factories.pipeline_factory import PipelineFactory

if __name__ == "__main__":

  """
  asset_bronze
  asset_silver
  asset_computed_silver
  asset_portfolio
  account_bronze
  account_silver
  """
  pipeline = PipelineFactory.get("asset_bronze")
  pipeline.run()


```
