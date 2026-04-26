# Commands

All commands are run from the `vault/` directory unless noted.

---

## Development

### FastAPI backend

```sh
uvicorn backend.api.main:app --reload --port 8001
```

### React frontend

```sh
cd frontend
npm run dev       # dev server on :5173
npm run build     # production build → frontend/dist/
```

### Dash dashboard (legacy)

```sh
python -m legacy.dashboard.app
```

---

## Pipeline

### Run a pipeline manually

```sh
python -m pipeline.orchestration.flow_t212_bronze
python -m pipeline.orchestration.flow_t212_silver
python -m pipeline.orchestration.flow_t212_gold
python -m pipeline.orchestration.flow_t212_history_bronze
python -m pipeline.orchestration.flow_fred
python -m pipeline.orchestration.flow_rebalance_plan
python -m pipeline.orchestration.asset_flow_portfolio
python -m pipeline.orchestration.enrichment_synchronization
```

---

## Prefect

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
| T212 history bronze | `prefect deployment run 'flow_t212_history_bronze/t212_history_bronze'` |
| FRED daily | `prefect deployment run 'flow_fred/fred_daily'` |
| Portfolio sync | `prefect deployment run 'flow_t212_asset_portfolio_sync/t212_asset_portfolio_sync'` |
| Enrichment sync | `prefect deployment run 'flow_t212_enrichment_sychronization/t212_enrichment_synchronization'` |
| Rebalance plan | `prefect deployment run 'flow_rebalance_plan/rebalance_plan'` |

### Prefect troubleshooting

```sh
prefect config view
prefect server stop
lsof -nP -iTCP:4200 -sTCP:LISTEN
kill -9 <PID>         # free port 4200 if server hangs
rm -rf ~/.prefect     # nuclear option — resets all prefect config
```

Create the work pool manually (already done by the deploy script):

```sh
prefect work-pool create asset-monitoring-pool --type process
```

### Point Prefect at the local server (once per environment)

```sh
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

---

## Database — Migrations

Migrations are split into five independent tracks, one per layer. Each has its own ini file in `vault/migrations/postgres/`.

All migration commands must be run from the `vault/` directory.

### Apply all migrations (fresh database)

```sh
alembic -c migrations/postgres/portfolio.ini upgrade head
alembic -c migrations/postgres/raw.ini upgrade head
alembic -c migrations/postgres/staging.ini upgrade head
alembic -c migrations/postgres/analytics.ini upgrade head
alembic -c migrations/postgres/monitoring.ini upgrade head
```

### Check status of all tracks

```sh
alembic -c migrations/postgres/raw.ini current
alembic -c migrations/postgres/staging.ini current
alembic -c migrations/postgres/analytics.ini current
alembic -c migrations/postgres/portfolio.ini current
alembic -c migrations/postgres/monitoring.ini current
```

### Create a new migration in a specific track

```sh
alembic -c migrations/postgres/staging.ini revision -m "<description>"
```

Replace `staging.ini` with the ini file for the layer you are modifying (`raw.ini`, `analytics.ini`, `portfolio.ini`, `monitoring.ini`).

### Apply a single track

```sh
alembic -c migrations/postgres/staging.ini upgrade head
```

### Downgrade a track

```sh
alembic -c migrations/postgres/staging.ini downgrade -1
```

### Stamp an existing database at head (no SQL executed)

Use this when the database is already migrated and you need to register the current state:

```sh
alembic -c migrations/postgres/raw.ini stamp <head-revision-id>
```

Get the head revision ID for a track:

```sh
alembic -c migrations/postgres/raw.ini heads
```

---

## Docker

```sh
docker compose down --remove-orphans
docker compose up -d
```

### Troubleshooting: Docker not starting (orphaned process)

```sh
ps aux | grep -i docker
kill -9 <process-id>
```

### Kafka: inspect consumer groups

```sh
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --all-groups
```

### Kafka: create topics

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

## Testing

```sh
ruff check .          # lint
ruff check --fix      # auto-fix lint issues
ruff rule F821        # look up a specific rule
```

---

## Git utilities

```sh
./scripts/git/sync_branch.sh
```

### Event consumer (run standalone)

```sh
python -m pipeline.infrastructure.kafka.consumer_main
```
