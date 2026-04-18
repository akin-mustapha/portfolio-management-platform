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
Frontend        frontend/                 React (Vite) — primary UI on :5172
                src/dashboard/            Dash UI — legacy dashboard on :8050
API             src/api/                  FastAPI — serves React frontend on :8001
Orchestration   src/orchestration/        Prefect — schedules pipelines
Backend         src/pipelines/            ETL pipelines and Kafka events
                src/backend/services/     Portfolio domain logic
Storage         raw → staging → analytics (Postgres, 3 schemas)
```

`src/shared/` and `src/config/` are cross-cutting utilities used by all layers.

The storage layer uses a medallion architecture inside Postgres:

| Schema      | Layer  | Description                                      |
|-------------|--------|--------------------------------------------------|
| `raw`       | Bronze | Append-only, partitioned by date, data as received |
| `staging`   | Silver | Typed, deduplicated, computed metrics            |
| `analytics` | Gold   | Kimball star schema — built to answer dashboard questions |

---

## Tech Stack

| Concern        | Tool                          |
|----------------|-------------------------------|
| React frontend | React, Vite, MUI, Recharts    |
| API            | FastAPI, Uvicorn              |
| Dash dashboard | Dash, Plotly, Dash Bootstrap  |
| Orchestration  | Prefect                       |
| Messaging      | Kafka (Confluent)             |
| Validation     | Pydantic                      |
| Database       | PostgreSQL, SQLModel, Alembic |
| HTTP Client    | HTTPX                         |
| Data           | Pandas                        |
| Testing        | Pytest                        |
| Runtime        | Python 3.13 / Node 20         |

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

### React frontend

```sh
cd frontend
npm install
npm run dev        # http://localhost:5172
```

### API (FastAPI)

```sh
uvicorn src.api.main:app --reload --port 8001
```

### Dash dashboard (legacy)

```sh
cd src
python -m dashboard.app   # http://localhost:8050
```

### Pipelines (via Prefect)

```sh
./scripts/deploy/prefect_deploy.sh
```

### Run a pipeline manually

```sh
cd src
python3 -m pipelines.application.runners.pipeline_bronze_t212
```

---

## Project Structure

```
frontend/               # React UI (Vite + MUI + Recharts) — port 5172
src/
├── api/                # FastAPI — serves the React frontend — port 8001
├── dashboard/          # Dash UI (legacy dashboard) — port 8050
├── orchestration/      # Prefect flows
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
