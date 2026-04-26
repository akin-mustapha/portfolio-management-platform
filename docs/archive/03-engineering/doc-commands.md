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
  kill -9 <PID>         # free port 4200 if server hangs
  rm -rf ~/.prefect     # nuclear option — resets all prefect config
```

### Migration

Migrations are split into 4 independent tracks, one per layer. Each has its own ini file in `migrations/postgres/`.

All migration commands must be run from the `vault/` directory.

#### Apply all migrations (fresh database)

```sh
  alembic -c migrations/postgres/portfolio.ini upgrade head
  alembic -c migrations/postgres/raw.ini upgrade head
  alembic -c migrations/postgres/staging.ini upgrade head
  alembic -c migrations/postgres/analytics.ini upgrade head
```

#### Check status of all tracks

```sh
  alembic -c migrations/postgres/raw.ini current
  alembic -c migrations/postgres/staging.ini current
  alembic -c migrations/postgres/analytics.ini current
  alembic -c migrations/postgres/portfolio.ini current
```

#### Create a new migration in a specific track

```sh
  alembic -c migrations/postgres/staging.ini revision -m "<description>"
```

Replace `staging.ini` with the ini file for the layer you are modifying (`raw.ini`, `analytics.ini`, `portfolio.ini`).

#### Downgrade a track

```sh
  alembic -c migrations/postgres/staging.ini downgrade -1
```

#### Stamp an existing database at head (no SQL executed)

Use this when the database is already migrated and you need to register the new tracks:

```sh
  alembic -c migrations/postgres/raw.ini stamp <head-revision-id>
  alembic -c migrations/postgres/staging.ini stamp <head-revision-id>
  alembic -c migrations/postgres/analytics.ini stamp <head-revision-id>
  alembic -c migrations/postgres/portfolio.ini stamp <head-revision-id>
```

Get the head revision ID for a track with: `alembic -c migrations/postgres/<layer>.ini heads`

### Prefect Deployment

Start the server, register all deployments, and start the worker:

```sh
bash scripts/deploy/prefect_deploy.sh
```

Re-register deployments after editing `prefect.yaml` (no restart needed):

```sh
prefect deploy --all
```

Inspect registered deployments:

```sh
prefect deployment ls
```

Manually trigger a flow run:

```sh
prefect deployment run '<flow-function-name>/<deployment-name>'
```

Current deployments:

| Deployment name | Command |
|---|---|
| T212 bronze | `prefect deployment run 'flow_t212_bronze/t212_bronze'` |
| T212 silver | `prefect deployment run 'flow_t212_silver/t212_silver'` |
| T212 gold | `prefect deployment run 'flow_t212_gold/t212_gold'` |
| Portfolio sync | `prefect deployment run 'flow_t212_asset_portfolio_sync/t212_asset_portfolio_sync'` |
| Enrichment sync | `prefect deployment run 'flow_t212_enrichment_sychronization/t212_enrichment_synchronization'` |
| Rebalance plan | `prefect deployment run 'flow_rebalance_plan/rebalance_plan'` |

Create the work pool manually (already done by the deploy script):

```sh
prefect work-pool create asset-monitoring-pool --type process
```

## Services

### Gold Pipelines

Run manually from the project root:

```sh
  python -m src.pipelines.application.runners.pipeline_gold_t212
```

### Dash UI

```sh
  python -m src.dashboard.app
```

## Util

### Sync branch

```sh
  ./scripts/git/sync_branch.sh
```

### HOW-TO

#### Create database client
