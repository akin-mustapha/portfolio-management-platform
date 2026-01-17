# Commands

## Migration

### Create new migration

```sh
  alembic revision -m "<descritpion>"
```

### Apply migration

```sh
  alembic upgrade head
```

### Downgrade migration

```sh
  alembic downgrade -2
```

## Ingestion Service

```sh
  python -m ingestion_service.service
```

## Tagging Service

```sh
  python -m tagging_service.service
```
