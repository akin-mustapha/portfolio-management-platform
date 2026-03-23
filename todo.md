# TODO — Unified Bronze Pipeline Restructuring

## Goal
Unify bronze ingestion into a single atomic snapshot pipeline. Silver and gold become pure
transformations over stored data — no API calls required to re-run them.

---

## Phase 1 — Migrations

- [ ] `migrations/postgres/versions/raw/003_raw_unified_snapshot.py`
  - Create `raw.trading212_raw` (snapshot_id TEXT, snapshot_at TIMESTAMPTZ, partition_date DATE,
    account_data JSONB, positions_data JSONB, processed_at TIMESTAMPTZ)
  - Partition by RANGE(partition_date), follow pattern from `001_raw_setup.py`
  - Create exposition views: `raw.v_bronze_positions`, `raw.v_bronze_account_v2`

- [ ] `migrations/postgres/versions/staging/012_staging_add_snapshot_id.py`
  - Add `snapshot_id TEXT` (nullable) to `staging.asset`
  - Add `snapshot_id TEXT` (nullable) to `staging.account`

---

## Phase 2 — New Unified Bronze Pipeline

- [ ] `src/backend/ingestion/application/pipelines/pipeline_bronze.py`
  - `Trading212BronzeSource.extract()` — calls both `equity/account/summary` and
    `equity/positions`; raises if either returns error (no partial writes)
  - `Trading212BronzeDestination.load()` — one INSERT into `raw.trading212_raw` with
    generated snapshot_id, account_data, positions_data
- [ ] `src/backend/ingestion/application/pipelines/loaders/bronze_unified_loader.py`
  - `BronzeUnifiedLoader(FullLoader)` — partition creation + exposition views
- [ ] Register `"bronze"` → `PipelineBronze` in `pipeline_factory.py`

---

## Phase 3 — Update Silver Sources

- [ ] `pipeline_asset_silver.py` — `Trading212AssetSourceSilver` reads from `raw.trading212_raw`
  WHERE `processed_at IS NULL`; unpacks `positions_data` JSONB array
- [ ] `pipeline_account_silver.py` — `Trading212AccountSourceSilver` reads from
  `raw.trading212_raw` WHERE `processed_at IS NULL`; unpacks `account_data` JSONB
- [ ] Both silver destinations — include `snapshot_id` in upsert payload

---

## Phase 4 — New Prefect Flow

- [ ] `src/orchestration/prefect/flow_t212_pipeline.py`
  - `task_bronze()` → `task_asset_silver()` + `task_account_silver()` →
    `task_asset_computed_silver()` + `task_account_computed_silver()` →
    `task_asset_gold()` + `task_account_gold()` → `task_mark_snapshot_processed()`
  - `task_mark_snapshot_processed()` — `UPDATE raw.trading212_raw SET processed_at = now()
    WHERE processed_at IS NULL` (only runs if all upstream succeed)

---

## Phase 5 — Cleanup

- [ ] Remove `pipeline_asset_bronze.py`, `pipeline_account_bronze.py`
- [ ] Remove `loaders/asset_full_loader.py`, `loaders/account_full_loader.py`
- [ ] Remove old factory registrations (`"asset_bronze"`, `"account_bronze"`)
- [ ] Retire old flows: `flow_t212_asset.py`, `flow_t212_account.py`, `account_flow_silver.py`
- [ ] Keep `raw.asset` and `raw.account` tables — do not drop until new pipeline has run

---

## Phase 6 — Tests

- [ ] `tests/ingestion/test_pipeline_bronze.py`
  - Bronze source calls both API endpoints
  - Raises if either endpoint returns error dict (no partial write)
  - Destination writes one row with correct snapshot_id, account_data, positions_data
- [ ] `tests/ingestion/test_silver_watermark.py`
  - Asset and account silver sources query `WHERE processed_at IS NULL`
  - processed_at remains NULL if silver fails mid-run

---

## Phase 7 — Doc Updates

- [ ] `docs/02-architecture/architecture.md` — update bronze: unified snapshot pipeline,
  `raw.trading212_raw` table
- [ ] `docs/02-architecture/design/schema/schema-staging.md` — add `snapshot_id TEXT` to
  asset and account table definitions
- [ ] `docs/02-architecture/design/ingestion/doc-pipelines.md` — document new bronze pattern

---

## Future Task — Move Historical Computations to Gold (Separate Branch)

Agreed: columns that require historical records (MAs, rolling volatility, drawdown) belong in
gold (`fact_technical`), not silver (`staging.asset_computed`). Silver should only hold
per-snapshot metrics.

When ready:
- Remove `ma_20d`, `ma_30d`, `ma_50d`, `volatility_*`, `var_95_1d` from
  `pipeline_asset_computed_silver.py`
- Compute these via SQL window functions in `AssetGoldSource` (reads from `staging.asset`
  price history)
- Migrations: drop MA columns from `staging.asset_computed`; `fact_technical` already has them
