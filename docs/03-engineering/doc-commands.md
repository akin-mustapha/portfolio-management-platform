# Commands

## Tools

### Docker

```sh
  docker compose down --remove-orphans
  docker compose up -d
```

#### Troubleshooting: Docker not starting (orphaned process)

```sh
  ps aux | grep -i docker
  kill -9 <process-id>
```

#### Kafka: inspect consumer groups

```sh
  kafka-consumer-groups --bootstrap-server localhost:9092 --describe --all-groups
```

#### Kafka: create topics

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

#### Prefect: troubleshooting

```sh
  prefect config view
  prefect server stop
  lsof -i :4200
  lsof -nP -iTCP:4200 -sTCP:LISTEN
  rm -rf ~/.prefect   # nuclear option — resets all prefect config
```

### Migration

```sh
  alembic init <migration name>
```

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

### Ingestion Pipeline

```sh
  python3 -m ingestion.pipelines.pipeline_account_bronze
```

### Tagging Service

```sh
  python3 -m scripts.run_tagging_service
```

### Dash UI

```sh
  python -m src.dashboard.app_2
```

## Util

### Sync branch

```sh
  ./scripts/git/sync_branch.sh
```

### HOW-TO

#### Create database client
