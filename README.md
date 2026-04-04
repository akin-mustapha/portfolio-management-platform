# Asset Monitoring System

A personal stock portfolio monitoring system. It pulls data from [Trading212](https://www.trading212.com/), processes it through a data pipeline, and surfaces it on a Dash dashboard — providing portfolio analytics and metrics that Trading212 doesn't offer natively.

---

## What It Does

- Ingests live and historical portfolio data from the Trading212 API
- Processes data through a bronze → silver medallion pipeline (raw → typed/deduplicated)
- Surfaces a dashboard with portfolio-level and asset-level analytics:
  - Total portfolio value, cost basis, and return (absolute and %)
  - Best and worst performing assets
  - Per-asset drawdown, volatility, moving averages, and DCA signals
  - Portfolio distribution and risk metrics

---

## Architecture

Four layers, each with a single responsibility:

```
Frontend        src/dashboard/            Dash UI — reads from services
Orchestration   src/orchestration/        Prefect — schedules pipelines
Backend         src/pipelines/    ETL pipelines and Kafka events
                src/backend/services/     Portfolio domain logic
Storage         raw → staging → analytics (Postgres, 3 schemas)
```

`src/shared/` and `src/config/` are cross-cutting utilities used by all layers.

The storage layer uses a medallion architecture inside Postgres:

| Schema      | Layer  | Description                                      |
|-------------|--------|--------------------------------------------------|
| `raw`       | Bronze | Append-only, partitioned by date, data as received |
| `staging`   | Silver | Typed, deduplicated, computed metrics            |
| `analytics` | Gold   | Built to answer dashboard questions (in progress) |

---

## Tech Stack

| Concern        | Tool                          |
|----------------|-------------------------------|
| Dashboard      | Dash, Plotly, Dash Bootstrap  |
| Orchestration  | Prefect                       |
| Messaging      | Kafka (Confluent)             |
| Validation     | Pydantic                      |
| Database       | PostgreSQL, SQLModel, Alembic |
| HTTP Client    | HTTPX                         |
| Data           | Pandas                        |
| Testing        | Pytest                        |
| Runtime        | Python 3.13                   |

---

## Prerequisites

- Python 3.13+
- Docker (for Kafka and Postgres)
- A [Trading212](https://www.trading212.com/) account with API access

---

## Setup

### 1. Clone and install dependencies

```sh
git clone <repo-url>
cd asset_monitoring_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```sh
touch .env
```

Add the following to `.env`:

```
API_URL=
API_TOKEN=
SECRET_TOKEN=
DATABASE_URL=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

### 3. Start infrastructure (Kafka + Postgres)

```sh
docker compose up -d
```

### 4. Run database migrations

```sh
alembic upgrade head
```

### 5. Create Kafka topics

```sh
docker exec -it kafka kafka-topics \
  --create --topic asset.ingestion \
  --bootstrap-server localhost:9092 \
  --partitions 1 --replication-factor 1

docker exec -it kafka kafka-topics \
  --create --topic analytics.ingestion \
  --bootstrap-server localhost:9092 \
  --partitions 1 --replication-factor 1
```

---

## Running

### Dashboard

```sh
cd src
python -m dashboard.app
```

### Pipelines (via Prefect)

```sh
./scripts/deploy/prefect_deploy.sh
```

### Run a pipeline manually

```sh
cd src
python3 -m pipelines.application.runners.pipeline_account_bronze
```

---

## Project Structure

```
src/
├── dashboard/          # Frontend — Dash UI
├── orchestration/      # Orchestration — Prefect flows
├── pipelines/          # ETL pipelines, Kafka producer/consumer
├── backend/
│   └── services/       # Portfolio domain logic
├── shared/             # Database client, migrations, utilities
└── config/             # App and environment configuration
```

---

## Development

### Migrations

```sh
# Create a new migration
alembic revision -m "<description>"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -2
```

### Tests

```sh
pytest
```

### Branching

Branches are linked to GitHub issues. Format: `feature/issue-123-description` or `bug/issue-42-description`. One layer per branch.

---

## Docs

| Document | Description |
|---|---|
| `docs/02-architecture/architecture.md` | Full architecture detail |
| `docs/02-architecture/design/ui-design.md` | Dashboard question catalogue |
| `docs/03-engineering/doc-setup.md` | Setup guide |
| `docs/03-engineering/doc-commands.md` | Common commands reference |
| `docs/03-engineering/doc-project-workflow.md` | Git and PR workflow |
