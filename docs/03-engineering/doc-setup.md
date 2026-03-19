---
name: Setup
description: Project setup documentation
---


# Setup

## Overview

Documenation of project set-up

## Create .env

- Create .env

```sh
  touch .env
```

- Make sure `.env` is in `gitignore`

### Variables

Add the following variables to env file

- API_URL
- API_TOKEN
- SECRET_TOKEN
- DATABASE_URL

## Start infrastructure

Start Postgres and Kafka via Docker:

```sh
docker compose up -d
```

## Prefect setup

Prefect 3 uses a persistent server, a work pool, and a worker process. Schedules are defined in `prefect.yaml` — not in the flow files.

### 1. Point Prefect at the local server

```sh
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

Only needed once per environment. Verify with `prefect config view`.

### 2. Start everything

```sh
bash scripts/deploy/prefect_deploy.sh
```

This script does four things:

1. Starts the Prefect server (UI at `http://127.0.0.1:4200`)
2. Creates the `asset-monitoring-pool` work pool (skips if it already exists)
3. Registers all deployments from `prefect.yaml` (`prefect deploy --all`)
4. Starts a process worker on the pool

### 3. Updating schedules or adding a new deployment

Edit `prefect.yaml`, then re-run:

```sh
prefect deploy --all
```

No restart required.

### Set Alembic ini

Migrations use four separate ini files, one per medallion layer. They all read `DATABASE_URL` from the `.env` file — no manual URL configuration needed.

To verify Alembic can connect and see the current state of all tracks:

```sh
alembic -c migrations/postgres/raw.ini current
alembic -c migrations/postgres/staging.ini current
alembic -c migrations/postgres/analytics.ini current
alembic -c migrations/postgres/portfolio.ini current
```

To apply all migrations on a fresh database:

```sh
alembic -c migrations/postgres/portfolio.ini upgrade head
alembic -c migrations/postgres/raw.ini upgrade head
alembic -c migrations/postgres/staging.ini upgrade head
alembic -c migrations/postgres/analytics.ini upgrade head
```

Full migration reference: `docs/02-architecture/design/doc-migration.md`
