# Architecture

Four layers. Each has a single responsibility.

```
┌─────────────────────────────────┐
│           Frontend              │  Dash UI — portfolio & asset views
├─────────────────────────────────┤
│         Orchestration           │  Prefect — schedules and coordinates pipelines
├─────────────────────────────────┤
│           Backend               │  Pipelines, events, services
├─────────────────────────────────┤
│           Storage               │  raw → staging → analytics
└─────────────────────────────────┘
```

---

## Frontend (`src/dashboard/`)

Dash application. Reads from the analytics (gold) layer via backend services.
Does no data transformation — only displays what services provide.

## Orchestration (`src/orchestration/`)

Prefect. Defines when and in what order pipelines run.
Sits above the backend — coordinates it, doesn't contain business logic.

## Backend (`src/backend/`)

**Ingestion** (`src/backend/ingestion/`) — Pulls data from Trading212 via events and pipelines. Loads into raw, transforms through to staging.

- `domain/` — core models: Data and Event
- `application/` — protocols, policies, all pipeline logic (bronze, silver, loaders, events)
- `infrastructure/` — external integrations: Trading212 API client, Kafka producer/consumer, database repositories
- `factories/` — PipelineFactory and EventProducerFactory registries

**Services** (`src/backend/services/`) — Business logic layer between storage and frontend.
Currently: `portfolio/` service.

- `domain/` — entities: Asset, Tag, Category, AssetTag, Industry, Sector
- `application/` — use case interfaces and repository contracts (protocols)
- `infrastructure/` — repository implementations (Postgres and SQLite) per entity

## Storage (`raw` → `staging` → `analytics`)

Three-schema medallion architecture inside Postgres.

| Schema | Also Called | What It Holds |
|--------|-------------|---------------|
| `raw` | Bronze | Append-only partitioned data, exactly as received |
| `staging` | Silver | Typed, deduplicated, computed metrics |
| `analytics` | Gold | Kimball star schema — built to answer dashboard questions |

Schema detail: `docs/02-architecture/design/schema/`

## Cross-cutting

`src/shared/` — database connections, repositories, utilities used across all layers.
`src/config/` — environment and app configuration.
