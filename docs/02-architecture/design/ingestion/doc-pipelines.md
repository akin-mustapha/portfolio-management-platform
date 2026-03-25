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

Each pipeline declares a Pydantic schema in `src/pipelines/domain/schemas/` representing the data contract for that pipeline. Schemas are independent of the database schema — they enforce types, coerce values, and reject invalid records before anything is written.

```python
from pydantic import BaseModel, ConfigDict, field_validator

class XYZRecord(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str
    value: float

    @field_validator("id")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v
```

Place schemas under:
- `domain/schemas/bronze/` — for API response shape checks (bronze pipelines)
- `domain/schemas/silver/` — for staging table contracts (silver pipelines)

## Convenience Base Classes

Rather than directly subclassing `Pipeline`, most concrete pipelines extend one of these:

**`BaseSilverPipeline`** — implements `run()` for the standard extract → transform → load flow. Override `_to_records()` to validate and map transformed dicts through a Pydantic schema. Invalid records are logged and skipped; the batch continues with valid records only. Use for silver-tier pipelines.

**`FullLoader`** — implements `run()` for bronze-tier bulk loads with date partitioning. Override `_create_partition()`, `_loader()`, and `_exposition_abstraction()`. Use for raw/bronze ingestion.

Both are defined in `src/pipelines/application/policies.py`.

## Computed Silver Pattern

Computed silver pipelines (`PipelineAssetComputedSilver`, `PipelineAccountComputedSilver`) follow a different pattern from standard silver pipelines:

| Aspect | Silver (`BaseSilverPipeline`) | Computed Silver (bare `Pipeline`) |
|--------|-------------------------------|-----------------------------------|
| Base class | `BaseSilverPipeline` | `Pipeline` |
| Output type | Pydantic model | Dataclass |
| Validation | `_to_records()` — logs and skips bad records | None — errors raise and halt |
| Source | Reads from silver table (full recompute) | Reads from silver table (full recompute) |
| Computation | Python transform | SQL window functions; Python handles null-coercion only |
| Unique key | `business_key` | Entity ID (`asset_id` / `account_id`) |

Use this pattern when metrics require window functions over the full history of a table (rolling averages, cumulative returns, LAG-based daily change). All computation lives in the SQL source query; Python only coerces nulls to 0 and maps rows to dataclasses.

## Gold Pattern

The canonical gold pipeline is `PipelineT212Gold` (`src/pipelines/application/runners/pipeline_gold_t212.py`). It is a unified pipeline that handles both asset-level and account-level facts in a single run.

**Key design decision:** All computation (window functions, rolling averages, LAG-based returns, volatility) is done in the SQL source query inside `PipelineT212Gold`. The pipeline reads directly from `staging.asset` and `staging.account` — it does **not** depend on `staging.asset_computed` or `staging.account_computed`.

**`BaseGoldPipeline`** — implements `run()` for gold pipelines that follow the standard fan-out pattern. Subclasses must declare:
- `_pipeline_name: str` — used in log messages and dead letter records
- `_fact_destinations: list[Destination]` — one destination per fact table

And wire `_source`, `_transformation`, `_validator`, `_dead_letter` in `__init__`.

The `run()` flow is:
1. `_ensure_dimensions()` — upsert dimension rows the source query FK-joins against
2. `extract()` — single source query joining staging and dim tables (with all window functions)
3. `transform()` — convert SQLAlchemy rows to plain dicts (no computation)
4. `validate()` — `SchemaValidator` separates valid records from rejected ones
5. Invalid records → `DeadLetterDestination` (written to `monitoring` schema)
6. Valid records → fan-out to all `_fact_destinations` (each projects only its columns)

**`SchemaValidator`** — generic validator used by gold (and can be used by silver) pipelines. Takes a Pydantic model and a `layer` string. Returns a `ValidationResult` with `valid` (model instances) and `invalid` (`RejectedRecord` objects). The pipeline sets `pipeline_name` on rejected records before passing them to `DeadLetterDestination`.

**`DeadLetterDestination`** — writes `RejectedRecord` objects to the `monitoring` schema. Used to capture records that fail schema validation without halting the pipeline. Defined in `src/pipelines/infrastructure/repositories/dead_letter_destination.py`.

Place gold schemas under:
- `domain/schemas/gold/` — for analytics fact table contracts

## How to Create a New Pipeline

All pipelines live under `src/pipelines/application/`. Sub-folders by type:
- `runners/` — all pipeline implementations (bronze, silver, gold)
- `loaders/` — bronze-tier full loaders
- `events/` — event producers and consumers

Follow these steps to implement a new pipeline:

1. **Define your data contract** — create a Pydantic schema in `domain/schemas/bronze/` or `domain/schemas/silver/` depending on the layer (see Validation section below)
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

## Validation

Pipelines use a two-layer validation approach. Each layer has a distinct schema location and a different failure behaviour.

| Layer | Schema location | On validation failure |
|---|---|---|
| Bronze | `domain/schemas/bronze/` | Raises — aborts the entire run |
| Silver | `domain/schemas/silver/` | Logs a warning, skips the bad record, batch continues |

**Bronze schemas** are structural API contracts. They check that required fields are present and have the expected types. `extra='allow'` is set so new fields added by the upstream API do not break the pipeline. A bronze validation failure means the API response is malformed — the run should not proceed.

**Silver schemas** are business contracts for staging tables. They enforce types, coerce values (e.g. `Decimal` to `float`), strip whitespace, and reject records with empty identity fields. A silver validation failure means one record is bad — the rest of the batch should still be written.

```python
# Bronze — fail fast
records = [AssetAPIRecord.model_validate(r) for r in raw_data]  # raises on failure

# Silver — fault-isolated, inside _to_records()
validated = []
for record in transformed:
    try:
        validated.append(AssetRecord.model_validate(record).model_dump())
    except ValidationError as e:
        logger.warning("Skipping invalid record: %s", e)
```

## Testing

- Test each ETL component (`Source`, `Transformation`, `Destination`) in isolation
- Mock dependencies when unit testing
- Write an integration test for the full `run` method using a test database or fixture data
- *(Link to test directory or testing guide here)*

## Naming

PipelineExampleSilver

## Storage

Specify any required database tables using DDL migrations. See the database migration reference below.

## Reference

**Database Migration**: See `docs/02-architecture/design/doc-migration.md`
**Ingestion Pipeline Architecture:** See `docs/02-architecture/assets/ingestion_pipeline_architecture_vx.x.x_latest.png`
