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
python3 -m scripts.run_ingestion_service
```

### Tagging Service

```sh
python3 -m scripts.run_tagging_service
```

## Util

### Sync branch

```sh
./scripts/git/sync_branch.sh
```
