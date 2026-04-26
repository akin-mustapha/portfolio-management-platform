# Refactor: Ingestion Clean Architecture

> **Status: Completed** — Implemented on branch `ingestion-cleanup-dead-code`. Retained as an ADR.
> **Historical note:** This document captures the migration from legacy `src/backend/ingestion` paths. Current runtime pipeline code lives in `src/pipelines`.

Restructure `src/backend/ingestion/` to comply with clean architecture — single `application/` and `infrastructure/` layer, flatten event modules.

---

## Target Structure

```
ingestion/
├── domain/
│   ├── __init__.py
│   └── models.py                        ← MERGED (Data + Event)
├── application/
│   ├── __init__.py
│   ├── protocols.py                     ← MOVED from app/
│   ├── policies.py                      ← MERGED (app/ + event_producer/app/ + event_consumer/app/)
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── interface_api_client.py      ← MOVED from app/interfaces/
│   │   └── interface_database_client.py ← MOVED + TYPO FIXED (was interace_)
│   └── pipelines/
│       ├── __init__.py
│       ├── pipeline_asset_bronze.py
│       ├── pipeline_account_bronze.py
│       ├── pipeline_asset_silver.py
│       ├── pipeline_account_silver.py
│       ├── pipeline_asset_computed_silver.py
│       ├── pipeline_asset_portfolio.py
│       ├── portfolio_enrichment_synchronizer.py
│       ├── loaders/
│       │   ├── __init__.py
│       │   ├── asset_full_loader.py
│       │   └── account_full_loader.py
│       └── events/
│           ├── __init__.py
│           ├── trading212_event_producer.py
│           └── trading212_asset_consumer.py
├── infrastructure/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── api_client_trading212.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── repository_factory.py
│   │   ├── repository_postgres.py
│   │   └── repository_sqlite.py
│   └── kafka/
│       ├── __init__.py
│       ├── producer_destination.py      ← RENAMED from event_producer/infra/destination.py
│       ├── producer_origins.py          ← RENAMED from event_producer/infra/origins.py
│       ├── consumer_adapter.py          ← RENAMED from event_consumer/infra/kafka_adapter.py
│       ├── consumer_db_client.py        ← RENAMED from event_consumer/infra/database/client.py
│       ├── consumer_main.py             ← MOVED from event_consumer/main.py
│       └── schema/
│           ├── asset_postgres.yml
│           ├── asset_snapshot.yml
│           ├── asset_sqlite.yml
│           └── dim_asset_postgres.yml
├── factories/
│   ├── __init__.py
│   ├── pipeline_factory.py              ← IMPORT PATHS UPDATED
│   └── event_producer_factory.py        ← MOVED from event_producer/ root
└── __init__.py
```

---

## File Mapping

| Old Path | New Path | Action |
|---|---|---|
| `app/domain.py` | `domain/models.py` | MERGE with event domain |
| `event_producer/app/domain.py` | `domain/models.py` | MERGE — `Event` added |
| `app/protocols.py` | `application/protocols.py` | MOVE |
| `app/policies.py` | `application/policies.py` | MERGE base |
| `event_producer/app/policies.py` | `application/policies.py` | MERGE — append `EventProducer`, `Origin`, `EventDestination` |
| `event_consumer/app/policies.py` | `application/policies.py` | MERGE — append `SchemeFactory`, `Mapper`, `EventConsumer`, `Repository` |
| `app/interfaces/interface_api_client.py` | `application/interfaces/interface_api_client.py` | MOVE |
| `app/interfaces/interace_database_client.py` | `application/interfaces/interface_database_client.py` | MOVE + FIX TYPO |
| `app/interfaces/interface_repository.py` | DELETE | One-line re-export shim — import from `shared` directly |
| `infra/api/api_client_trading212.py` | `infrastructure/api/api_client_trading212.py` | MOVE |
| `infra/repositories/repository_factory.py` | `infrastructure/repositories/repository_factory.py` | MOVE |
| `infra/repositories/repository_postgres.py` | `infrastructure/repositories/repository_postgres.py` | MOVE |
| `infra/repositories/repository_sqlite.py` | `infrastructure/repositories/repository_sqlite.py` | MOVE |
| `pipelines/pipeline_asset_bronze.py` | `application/pipelines/pipeline_asset_bronze.py` | MOVE |
| `pipelines/pipeline_account_bronze.py` | `application/pipelines/pipeline_account_bronze.py` | MOVE |
| `pipelines/pipeline_asset_silver.py` | `application/pipelines/pipeline_asset_silver.py` | MOVE |
| `pipelines/pipeline_account_silver.py` | `application/pipelines/pipeline_account_silver.py` | MOVE |
| `pipelines/pipeline_asset_computed_silver.py` | `application/pipelines/pipeline_asset_computed_silver.py` | MOVE |
| `pipelines/pipeline_asset_portfolio.py` | `application/pipelines/pipeline_asset_portfolio.py` | MOVE |
| `pipelines/portfolio_enrichment_synchronizer.py` | `application/pipelines/portfolio_enrichment_synchronizer.py` | MOVE |
| `pipelines/pipeline_asset_gold.py` | DELETE | Stub only — no content |
| `full_loader/asset_full_loader.py` | `application/pipelines/loaders/asset_full_loader.py` | MOVE |
| `full_loader/account_full_loader.py` | `application/pipelines/loaders/account_full_loader.py` | MOVE |
| `event_producer/app/trading212_event_producer.py` | `application/pipelines/events/trading212_event_producer.py` | MOVE |
| `event_consumer/trading212_asset_consumer.py` | `application/pipelines/events/trading212_asset_consumer.py` | MOVE |
| `event_producer/infra/destination.py` | `infrastructure/kafka/producer_destination.py` | MOVE + RENAME |
| `event_producer/infra/origins.py` | `infrastructure/kafka/producer_origins.py` | MOVE + RENAME |
| `event_consumer/infra/kafka_adapter.py` | `infrastructure/kafka/consumer_adapter.py` | MOVE + RENAME |
| `event_consumer/infra/database/client.py` | `infrastructure/kafka/consumer_db_client.py` | MOVE + RENAME |
| `event_consumer/schema/*.yml` | `infrastructure/kafka/schema/*.yml` | MOVE |
| `event_consumer/main.py` | `infrastructure/kafka/consumer_main.py` | MOVE + RENAME |
| `event_producer/event_producer_factory.py` | `factories/event_producer_factory.py` | MOVE |
| `factories/pipeline_factory.py` | `factories/pipeline_factory.py` | UPDATE IMPORTS ONLY |
| `factories/full_loader_factory.py` | DELETE | Empty file |

---

## Key Merge Notes

### `domain/models.py`
Combine `Data` (from `app/domain.py`) and `Event` (from `event_producer/app/domain.py`) into one file. No overlap — both dataclasses are independent. Re-export both from `domain/__init__.py`.

### `application/policies.py`
Three files merge here. **Name collision**: both `protocols.py` and `event_producer/app/policies.py` define a class named `Destination` with different signatures (`load()` vs `send()`). Resolve by renaming the event-flavour one to `EventDestination` in the merged file. Update all consumers:
- `trading212_event_producer.py` → import `EventDestination`
- `producer_destination.py` → import `EventDestination`

---

## Import Changes by File

### `infrastructure/api/api_client_trading212.py`
```python
# OLD
from ...app.interfaces.interface_api_client import APIClient
# NEW
from ...application.interfaces.interface_api_client import APIClient
```

### `application/pipelines/pipeline_asset_bronze.py` (and account)
```python
# OLD
from ..app.protocols import Source, Destination
from ..app.policies import Pipeline
from ..full_loader.asset_full_loader import PostgresAssetFullLoader
from ..infra.api.api_client_trading212 import Trading212APIClient
# NEW
from ...application.protocols import Source, Destination
from ...application.policies import Pipeline
from .loaders.asset_full_loader import PostgresAssetFullLoader
from ...infrastructure.api.api_client_trading212 import Trading212APIClient
```

### `application/pipelines/pipeline_asset_silver.py` (and account, computed)
```python
# OLD
from ..app.policies import BaseSilverPipeline
from ..app.protocols import Source, Transformation, Destination
from ..infra.repositories.repository_factory import RepositoryFactory
# NEW
from ...application.policies import BaseSilverPipeline
from ...application.protocols import Source, Transformation, Destination
from ...infrastructure.repositories.repository_factory import RepositoryFactory
```

### `application/pipelines/loaders/asset_full_loader.py`
```python
# OLD
from ..app.policies import FullLoader
# NEW
from ....application.policies import FullLoader
```

### `application/pipelines/events/trading212_event_producer.py`
```python
# OLD
from .policies import Origin, Destination, EventProducer
from .domain import Event
# NEW
from ....application.policies import Origin, EventDestination, EventProducer
from ....domain import Event
```

### `application/pipelines/events/trading212_asset_consumer.py`
```python
# OLD
from .app.policies import EventConsumer, Mapper
from .infra.database.client import DestinationFactory
# NEW
from ....application.policies import EventConsumer, Mapper
from ....infrastructure.kafka.consumer_db_client import DestinationFactory
```

### `infrastructure/kafka/producer_origins.py`
```python
# OLD (absolute)
from backend.ingestion.infra.api.api_client_trading212 import Trading212APIClient
from ..app.policies import Origin
# NEW (absolute)
from backend.ingestion.infrastructure.api.api_client_trading212 import Trading212APIClient
from ...application.policies import Origin
```

### `infrastructure/kafka/producer_destination.py`
```python
# OLD
from ..app.domain import Event
from ..app.policies import Destination
# NEW
from ...domain import Event
from ...application.policies import EventDestination
```

### `infrastructure/kafka/consumer_adapter.py`
```python
# OLD
from ..trading212_asset_consumer import Trading212AssetConsumer
# NEW
from ...application.pipelines.events.trading212_asset_consumer import Trading212AssetConsumer
```

### `infrastructure/kafka/consumer_main.py`
```python
# OLD (absolute)
from backend.ingestion.event_consumer.infra.kafka_adapter import KafkaAdapter
# NEW (absolute)
from backend.ingestion.infrastructure.kafka.consumer_adapter import KafkaAdapter
```

### `factories/pipeline_factory.py`
```python
# OLD
from ..app.policies import Pipeline
from ..pipelines.pipeline_asset_bronze import PipelineAssetBronze
# (etc.)
# NEW
from ..application.policies import Pipeline
from ..application.pipelines.pipeline_asset_bronze import PipelineAssetBronze
# (etc.)
```

### `factories/event_producer_factory.py`
```python
# OLD
from .app.policies import EventProducer
from .app.trading212_event_producer import Trading212EventProducer
from .infra.origins import Trading212AssetAPIOrigin
from .infra.destination import Trading212KafkaDestination
# NEW
from ..application.policies import EventProducer
from ..application.pipelines.events.trading212_event_producer import Trading212EventProducer
from ..infrastructure.kafka.producer_origins import Trading212AssetAPIOrigin
from ..infrastructure.kafka.producer_destination import Trading212KafkaDestination
```

---

## External Callers (Orchestration)

These files outside `ingestion/` require import updates:

| File | Change Required |
|---|---|
| `src/orchestration/prefect/enrichment_synchronization.py` | `from backend.ingestion.pipelines.portfolio_enrichment_synchronizer` → `from backend.ingestion.application.pipelines.portfolio_enrichment_synchronizer` |
| `src/orchestration/prefect/asset_flow_event_producer.py` | `from backend.ingestion.event_producer.event_producer_factory` → `from backend.ingestion.factories.event_producer_factory` |

All other orchestration flows (`flow_t212_asset`, `flow_t212_account`, `asset_flow_portfolio`) import only from `factories/pipeline_factory.py` which does not move — no changes needed.

---

## Implementation Phases

**Phase 1 — Create skeleton** (empty `__init__.py` only, nothing deleted)
- Create `domain/`, `application/`, `application/interfaces/`, `application/pipelines/`, `application/pipelines/loaders/`, `application/pipelines/events/`, `infrastructure/`, `infrastructure/api/`, `infrastructure/repositories/`, `infrastructure/kafka/`, `infrastructure/kafka/schema/`

**Phase 2 — Populate `domain/`**
- Create `domain/models.py` merging `Data` and `Event`
- Create `domain/__init__.py` re-exporting both

**Phase 3 — Populate `application/`**
- Copy `app/protocols.py` → `application/protocols.py`
- Create `application/policies.py` merging three policy files; rename `Destination` → `EventDestination`
- Copy interface files to `application/interfaces/` (fix filename typo)

**Phase 4 — Populate `infrastructure/`**
- Copy API client, update import
- Copy repository files
- Copy and rename all kafka files; update all imports

**Phase 5 — Populate `application/pipelines/`**
- Copy all pipeline files; update imports
- Copy loader files; update imports
- Copy event orchestration files; update imports

**Phase 6 — Update `factories/`**
- Update `pipeline_factory.py` imports in-place
- Move `event_producer_factory.py` to `factories/`; update its imports

**Phase 7 — Update external callers**
- Update two orchestration files (see table above)

**Phase 8 — Verify**
- Import-check all orchestration flow modules
- Run each `PipelineFactory.get()` and `EventProducerFactory.get()` in dry run

**Phase 9 — Delete old structure**
- Delete `app/`, `infra/`, `pipelines/`, `full_loader/`, `event_producer/`, `event_consumer/`
- Confirm nothing references old paths
