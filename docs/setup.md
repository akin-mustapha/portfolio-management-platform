# Setup

All commands are run from the `vault/` directory unless noted.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop

---

## Installation

### Python dependencies

```sh
cd vault
pip install -r requirements.txt    # or: pip install -e .
```

### Frontend dependencies

```sh
cd vault/frontend
npm install
```

---

## Environment variables

Create a `.env` file in the `vault/` directory (it is gitignored):

```sh
touch vault/.env
```

Required variables:

```
# Trading212
API_URL=
API_TOKEN=

# Application
SECRET_TOKEN=

# Postgres
DATABASE_URL=postgresql://user:password@localhost:5432/portfolio
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# FRED API
FREED_API_KEY=

# Email (for rebalance plan notifications)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
NOTIFICATION_EMAIL=

# AI analyst (optional)
ANTHROPIC_API_KEY=
```

---

## Running locally

### 1. Start infrastructure (Postgres + Kafka)

```sh
docker compose up -d
```

### 2. Apply database migrations

From `vault/`:

```sh
alembic -c migrations/postgres/portfolio.ini upgrade head
alembic -c migrations/postgres/raw.ini upgrade head
alembic -c migrations/postgres/staging.ini upgrade head
alembic -c migrations/postgres/analytics.ini upgrade head
alembic -c migrations/postgres/monitoring.ini upgrade head
```

### 3. Start the FastAPI backend

```sh
uvicorn backend.api.main:app --reload --port 8001
```

### 4. Start the React frontend

```sh
cd frontend
npm run dev    # http://localhost:5173
```

The frontend proxies `/api` requests to the FastAPI backend at `:8001`.

### 5. Start Prefect (optional — for pipeline scheduling)

```sh
bash scripts/deploy/prefect_deploy.sh
```

This script:
1. Starts the Prefect server (UI at `http://127.0.0.1:4200`)
2. Creates the `asset-monitoring-pool` work pool (skips if it already exists)
3. Registers all deployments from `prefect.yaml`
4. Starts a process worker on the pool

Only needed once per environment — point Prefect at the local server first:

```sh
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

---

## Running with Docker

```sh
docker compose up -d
```

See `docker-compose.yml` at the repo root for the full service definition.

---

## Verify migrations are current

```sh
alembic -c migrations/postgres/raw.ini current
alembic -c migrations/postgres/staging.ini current
alembic -c migrations/postgres/analytics.ini current
alembic -c migrations/postgres/portfolio.ini current
alembic -c migrations/postgres/monitoring.ini current
```

Full migration reference: `docs/design/doc-pipelines.md`
Full command reference: `docs/commands.md`
