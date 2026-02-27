# README

## Commands

## Tools

### Migration

#### Create new migration

```sh
  alembic revision -m "<descritpion>"
```

#### Apply migration

```sh
alembic upgrade head
```

#### Downgrade migration

```sh
alembic downgrade -2
```

### Prefect Deployment

```sh
./deploy/prefect_deploy.sh
```

## Services

### Ingestion Service

```sh
python3 -m src.services.ingestion.pipelines.pipeline_asset_portfolio
```

### Portfolio Service

```sh
python3 -m src.services.portfolio.service
```

## Util

### Sync branch

```sh
./scripts/git/sync_branch.sh
```
