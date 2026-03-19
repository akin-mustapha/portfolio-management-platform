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

## Set Prefect server port

- deploy/prefect_deploy.sh
- Start Kafka
- Start Consumer

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
