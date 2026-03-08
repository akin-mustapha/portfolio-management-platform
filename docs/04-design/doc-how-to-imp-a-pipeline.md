---
name: how to implement a pipeline
description: The documentation covers the workflow followed to create a new pipeline in this project
---

# What

Documentation for pipeline creation. Data pipelines are a simple scripts that defines data extraction logic, transformation steps and loading to destination database.

This project defines a `Pipeline` abstract class which all concrete implementation of the each pipeline inherit from.

`Pipeline` class define one abstract method `run`, each subclass implements this methods. This gives each subclass the freedom to skip any of the ETL steps, e.g., `XYZPipeline` implements a source, and destination, but no transformation step, an EL

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

Each `Pipeline` module declares a dataclass, usually this object has a simpler shape to the physcially data store shape, however they are in no way related.

## ETL

The ingestion project declares protocol which enforces the ETL process using python protocol.

**Source**: `Source` should implement an `extract` method, has specified by the protocol

**Transformation**: Should implement a `transform` method.

**Destination**: Should implement a `load` method.

```python
class XYZSource

class XYZTranformation

class XYZDestination

class XYZPipelin(Pipeline):
  def __init__(self, source: Source, transformation: Transformation destination: Destination):
    ....

  def run(self):
      data = self._source.extract()
      data = self._transformation.transform(data)
      self._destination.load(data)
```

## Storage

Specify database DDL, see database migration reference

## Reference

**Database Migration**: See `docs/04-design/doc-migration.md`
