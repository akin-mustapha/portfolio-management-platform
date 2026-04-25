# Plan: Finish bronze exposition views for T212 history

## Context

The branch `218-bronze-pipeline` introduces three cursor-paginated raw tables
(`raw.t212_history_dividend`, `raw.t212_history_order`,
`raw.t212_history_transaction`) and bronze exposition views on top of them so
downstream layers and EDA queries can read typed columns instead of probing
JSONB. Two views are partially built and one is missing. The goal is to finish
mapping the remaining columns from the real T212 payload shapes and wire the
third view into the loader.

Sample payloads supplied by the user (observed in production):

- **Dividend**: `{type, amount, paidOn, ticker, currency, quantity, reference,
  amountInEuro, grossAmountPerShare, instrument:{isin,name,ticker,currency}}`
- **Order** (HistoricalOrder wrapper): `{fill:{id,type,price,filledAt,quantity,
  walletImpact:{taxes:[{name,currency,quantity,chargedAt}], fxRate,currency,
  netValue}, tradingMethod}, order:{id,side,type,value,status,ticker,currency,
  strategy,createdAt,instrument:{isin,name,ticker,currency},filledValue,
  extendedHours,initiatedFrom}}`
- **Transaction**: no live sample yet. Per user decision, the transaction
  view is **deferred** until a real `/equity/history/transactions` payload is
  pasted in, so all columns can be mapped in one pass.

## What is done vs. what is left

### Dividend view — [v_bronze_dividend.sql](../../src/pipelines/infrastructure/queries/bronze/v_bronze_dividend.sql)

Done: every field in the sample payload is extracted with correct casts.
Left:

- Business key is redundant: `reference` is already the unique event id
  (it's also the primary key used by the loader in `_extract_id`).
  Replace `business_key` with just `reference AS business_key` for clarity,
  or drop the column entirely.

**Column names kept as-is** (`amountineuro`, `grossamountpershare`) per
user decision, to avoid breaking [sandbox/eda/queries/dividend.sql](../../sandbox/eda/queries/dividend.sql).
Accept the local inconsistency with snake_case used elsewhere.

### Order view — [v_bronze_order.sql](../../src/pipelines/infrastructure/queries/bronze/v_bronze_order.sql)

Has a `# TODO: DATA TYPE CONVERSION, FIX TAXES (LIST)` header — both issues
are real. Left to do:

1. **Fix wrong JSON keys** against the actual payload:
   - `payload->'fill'->>'at'` (line 9, aliased `file_at`) — wrong key and
     typo. Should be `payload->'fill'->>'filledAt'` aliased `filled_at`.
   - `payload->'fill'->>'trade'` (line 7, aliased `trade`) — no such key in
     payload. Remove; `trading_method` (line 19) already covers this.
   - `payload->>'order' AS order` (line 20) — `order` is a SQL reserved word
     and the column just dumps a nested JSON blob. Remove.
2. **Fix taxes (list) extraction** — `walletImpact.taxes` is a JSON array.
   Lines 12-15 use `->>'name'` on the array, which returns NULL. Two options:
   - Keep taxes as an aggregated array column (simpler, 1 row per order):
     expose `wallet_impact_taxes` (the raw JSONB array) plus scalar
     convenience columns for the common case of a single tax row, using
     `(payload->'fill'->'walletImpact'->'taxes'->0->>'name')` etc.
   - Use `jsonb_array_elements` in a `LATERAL` join to fan out one row per
     tax entry (changes cardinality — do not do this in the bronze view).
   - **Recommendation**: the first approach. Bronze views preserve 1:1 event
     shape; tax fan-out belongs in silver.
3. **Add type casts** on all numeric/timestamp/bool columns currently stored
   as TEXT:
   - `price`, `quantity`, `wallet_impact_fx_rate`, `wallet_impact_net_value`,
     `order_value`, `order_filled_value`, `wallet_impact_taxes_quantity` →
     `::NUMERIC`
   - `filled_at`, `order_created_at`, `wallet_impact_taxes_charged_at` →
     `::TIMESTAMPTZ`
   - `order_extended_hours` → `::BOOLEAN`
   (Match the casting style already used in `v_bronze_position.sql` and
   `v_bronze_dividend.sql`.)
4. **Fix the `name` column alias** (line 35): currently aliased `name` but
   it's the order instrument name. Rename to `order_instrument_name` for
   symmetry with `order_instrument_ticker`, `order_instrument_isin`, etc.
   (`sandbox/eda/queries/orders.sql` already references
   `order_instrument_name`, so the EDA query is currently broken against
   the view as written — this rename fixes it.)
5. **Business key**: `fill.id` (top-level `id`) is already unique per fill
   event and is what `_extract_id` uses to key the raw row. Replace the
   concatenation with `"id" AS business_key` or drop the column.
6. Remove the `# TODO` header comment once the above is done (it's inside a
   `CREATE OR REPLACE VIEW` — Postgres will accept leading `--` comments but
   the `#` is actually invalid SQL syntax and must be removed).

### Transaction view — **deferred**

Per user, hold off on creating `v_bronze_transaction.sql` and on wiring it
into the loader until a live `/equity/history/transactions` payload is
pasted in. The only reference in the repo today is the integration test
fixture (`reference, dateTime, amount, currency, type`), which is not
enough to guarantee all fields (likely also `accountId`, `fxRate`, possibly
`instrument`) are mapped. Revisit as a follow-up once a sample is in hand.

### Loader wiring — [loader_bronze_t212_history.py:113](../../src/pipelines/application/runners/loaders/loader_bronze_t212_history.py#L113)

`FullLoader.load()` in [policies.py:127](../../src/pipelines/application/policies.py#L127)
already invokes `_exposition_abstraction()` on every run, so no wiring
changes are needed in this pass. Add the third transaction-view drop/create
in the follow-up when the transaction view lands.

## Critical files to modify

- [src/pipelines/infrastructure/queries/bronze/v_bronze_dividend.sql](../../src/pipelines/infrastructure/queries/bronze/v_bronze_dividend.sql) — clean up `business_key` only
- [src/pipelines/infrastructure/queries/bronze/v_bronze_order.sql](../../src/pipelines/infrastructure/queries/bronze/v_bronze_order.sql) — significant rework (keys, taxes, casts, header comment, `name` alias)

(No other files touched in this pass — loader and transaction view are
deferred.)

## Patterns and utilities to reuse

- Cast style (`(payload->>'x')::NUMERIC`, `::TIMESTAMP`) — see
  [v_bronze_position.sql](../../src/pipelines/infrastructure/queries/bronze/v_bronze_position.sql)
  and [v_bronze_dividend.sql](../../src/pipelines/infrastructure/queries/bronze/v_bronze_dividend.sql)
- View template convention: `WITH cte AS (...) SELECT *, <business_key> FROM cte`,
  all four existing bronze views follow this shape
- `{table_name}` placeholder substituted by `loader.format(...)` in
  `_exposition_abstraction` — reuse, don't hardcode

## Verification

1. Apply the changes and run the bronze history pipeline:
   `python -m src.pipelines.application.runners.pipeline_bronze_t212_history`
   (or trigger via Prefect). `FullLoader.load()` recreates the views at the
   end of every run, so no manual SQL is needed.
2. In psql, smoke-test the updated views:
   - `SELECT * FROM raw.v_bronze_dividend LIMIT 5;`
   - `SELECT * FROM raw.v_bronze_order LIMIT 5;` — verify `filled_at` parses
     as timestamp, `price`/`quantity` are numeric, `wallet_impact_taxes` is
     JSONB, `order_instrument_name` is populated.
3. Run the existing bronze history integration test to confirm nothing
   regressed: `pytest tests/ingestion/integration/test_t212_history_raw_integration.py`.
4. Re-run `sandbox/eda/queries/orders.sql` end-to-end against the updated
   order view — the `order_instrument_name` alias rename should unbreak it.
5. Re-run `sandbox/eda/queries/dividend.sql` — should be unchanged since
   dividend column names were preserved.

## Follow-up (out of scope for this change)

Once a live transaction payload is available, a small follow-up will:

- Add `src/pipelines/infrastructure/queries/bronze/v_bronze_transaction.sql`
- Extend `FullLoaderPostgresT212History._exposition_abstraction` with a
  third drop/create for `raw.v_bronze_transaction`
- Add a `sandbox/eda/queries/transactions.sql` smoke query
