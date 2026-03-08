---
name: Pipeline Design
description: The documentation covers the workflow followed to create a new pipeline in this project
---

# Overview

Documentation for pipeline creation. Data pipelines are simple scripts that define data extraction logic, transformation steps, and loading to a destination database.

This project defines a `Pipeline` abstract class which all concrete implementations of each pipeline inherit from.

## ETL Components

Before implementing a pipeline, understand the three ETL components this project uses. Each is defined as a Python protocol, enforcing a consistent interface across all pipelines.

**Source**: Responsible for data extraction. Must implement an `extract` method that returns raw data.

**Transformation**: Responsible for reshaping or cleaning data. Must implement a `transform` method that accepts and returns data.

**Destination**: Responsible for loading data. Must implement a `load` method that accepts transformed data and writes it to the destination.

```python
class XYZSource(Source):
    def extract(self) -> list[XYZData]:
        # fetch raw data from source
        ...

class XYZTransformation(Transformation):
    def transform(self, data: list[XYZData]) -> list[XYZData]:
        # apply transformation logic
        ...

class XYZDestination(Destination):
    def load(self, data: list[XYZData]) -> None:
        # write data to destination database
        ...
```

## Pipeline Abstract Class

The `Pipeline` abstract class defines one abstract method `run`. Each subclass implements this method, giving it the freedom to skip any ETL steps — for example, `XYZPipeline` may implement only a source and destination with no transformation step (an EL pipeline).

```python
class Pipeline(ABC):
    _source: Source
    _transformation: Transformation
    _destination: Destination

    @abstractmethod
    def run(self):
        raise NotImplementedError
```

## Data Model

Each `Pipeline` module declares a dataclass representing the data passed between ETL steps. This object typically has a simpler shape than the physical data store — for example, it may flatten nested structures or omit fields not relevant to the pipeline. These dataclasses are independent of the database schema.

```python
@dataclass
class XYZData:
    id: str
    value: float
    # add fields relevant to this pipeline
```

## How to Create a New Pipeline

Follow these steps to implement a new pipeline:

1. **Define your data model** — create a dataclass in your pipeline module representing the data shape
2. **Implement `Source`** — create a class implementing the `extract` method
3. **Implement `Transformation`** — create a class implementing the `transform` method (skip if not needed)
4. **Implement `Destination`** — create a class implementing the `load` method
5. **Implement the `Pipeline` subclass** — wire the components together in the `run` method
6. **Write database DDL** — define any required tables (see Database Migration reference below)
7. **Write tests** — cover each ETL component independently and test the full `run` method

### Full Example

```python
class XYZPipeline(Pipeline):
    def __init__(
        self,
        source: Source,
        transformation: Transformation,
        destination: Destination
    ):
        self._source = source
        self._transformation = transformation
        self._destination = destination

    def run(self):
        data = self._source.extract()
        data = self._transformation.transform(data)
        self._destination.load(data)
```

## Error Handling

- If `extract` fails, the pipeline should raise and not proceed to transformation or loading
- If `transform` fails, the pipeline should raise and not proceed to loading
- *(Document any retry logic or failure recovery strategy here)*

## Testing

- Test each ETL component (`Source`, `Transformation`, `Destination`) in isolation
- Mock dependencies when unit testing
- Write an integration test for the full `run` method using a test database or fixture data
- *(Link to test directory or testing guide here)*

## Storage

Specify any required database tables using DDL migrations. See the database migration reference below.

## Reference

**Database Migration**: See `docs/04-design/doc-migration.md`
**Ingestion Pipeline Architecture:** See `docs/03-architecture/ingestion_pipeline_architecture_vx.x.x_latest.png`
