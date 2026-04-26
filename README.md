# Portfolio Management Platform

A personal stock portfolio monitoring platform. Pulls data from [Trading212](https://www.trading212.com/), processes it through a medallion ETL pipeline, and surfaces it on a React dashboard with analytics Trading212 doesn't provide natively.

---

## What It Does

- Ingests live and historical portfolio data from the Trading212 API
- Processes data through bronze → silver → gold layers (raw → staging → analytics)
- Serves a React dashboard with portfolio and asset-level metrics:
  - Total value, cost basis, and return (absolute and %)
  - Per-asset drawdown, volatility, moving averages, and DCA signals
  - Portfolio distribution and risk metrics

---

## Architecture

```
Frontend        vault/frontend/               React (Vite + MUI) — :5173
API             vault/backend/                FastAPI — :8001
Orchestration   vault/pipeline/orchestration/ Prefect — :4200
Pipeline        vault/pipeline/etl/           ETL (bronze → silver → gold)
Storage         raw → staging → analytics     Postgres (3 schemas)
```

| Schema      | Layer  | Description                                        |
|-------------|--------|----------------------------------------------------|
| `raw`       | Bronze | Append-only, partitioned by date, data as received |
| `staging`   | Silver | Typed, deduplicated, normalised                    |
| `analytics` | Gold   | Kimball star schema — built for dashboard queries  |

---

## Tech Stack

| Concern        | Tool                          |
|----------------|-------------------------------|
| Frontend       | React, Vite, MUI, Recharts    |
| API            | FastAPI, Uvicorn              |
| Orchestration  | Prefect                       |
| Validation     | Pydantic                      |
| Database       | PostgreSQL, SQLModel, Alembic |
| Testing        | Pytest                        |
| Runtime        | Python 3.13 / Node 20         |

---

## Prerequisites

- Python 3.13+
- Node 20+
- Docker (for Postgres)
- A [Trading212](https://www.trading212.com/) account with API access

---

## Setup

```sh
git clone <repo-url>
cd portfolio-management-platform/vault
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in credentials
docker compose up -d
alembic -c migrations/postgres/alembic_raw.ini upgrade head
alembic -c migrations/postgres/alembic_staging.ini upgrade head
alembic -c migrations/postgres/alembic_analytics.ini upgrade head
alembic -c migrations/postgres/alembic_portfolio.ini upgrade head
```

See `docs/setup.md` for full environment variable reference.

---

## Running

```sh
# React frontend
cd vault/frontend && npm install && npm run dev   # http://localhost:5173

# FastAPI
cd vault && uvicorn backend.api.main:app --reload --port 8001

# Prefect pipelines
cd vault && prefect deploy --all
```

---

## Docs

| Document | Description |
| --- | --- |
| `docs/architecture.md` | Layer diagram and key decisions |
| `docs/setup.md` | Full setup guide |
| `docs/commands.md` | Common commands |
| `docs/design/doc-pipelines.md` | Pipeline pattern reference |
| `docs/design/schema-analytics.md` | Gold schema reference |
| `docs/design/schema-staging.md` | Silver schema reference |
| `docs/design/metrics-reference.md` | Dashboard metrics catalogue |
