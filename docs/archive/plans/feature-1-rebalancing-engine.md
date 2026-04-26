# Feature 1 — Rebalancing Engine

## Context

The system currently reads and visualises portfolio data but offers no decision support for managing allocations. This adds a Rebalancing Engine: the user configures per-asset target weights and risk settings from a dashboard panel, and the system generates a multi-day correction plan and emails it daily. Plan-only mode — no trade execution. Execution can be wired in later.

## Branching

| Branch | Layer | Merges before |
|---|---|---|
| `feature/issue-156-rebalance-schema` | Storage | — |
| `feature/issue-156-rebalance-service` | Backend | schema merged |
| `feature/issue-156-rebalance-dashboard` | Dashboard + Orchestration | service merged |

---

## Day 1 — Database

**New file:** `migrations/postgres/versions/portfolio/009_rebalance_tables.py`

```
revision:      4400000000d9
down_revision: 4400000000d8
```

### Table: `portfolio.rebalance_config`

One row per asset. Stores the user's target allocation and rebalancing behaviour settings.

```sql
CREATE TABLE portfolio.rebalance_config (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id                UUID NOT NULL REFERENCES portfolio.asset(id),
    target_weight_pct       NUMERIC(5,2) NOT NULL,
    min_weight_pct          NUMERIC(5,2) NOT NULL DEFAULT 0.0,
    max_weight_pct          NUMERIC(5,2) NOT NULL DEFAULT 100.0,
    risk_tolerance          SMALLINT NOT NULL DEFAULT 50
                                CHECK (risk_tolerance BETWEEN 0 AND 100),
    rebalance_threshold_pct NUMERIC(5,2) NOT NULL DEFAULT 2.0,
    correction_days         SMALLINT NOT NULL DEFAULT 3
                                CHECK (correction_days BETWEEN 1 AND 7),
    momentum_bias           SMALLINT NOT NULL DEFAULT 0
                                CHECK (momentum_bias BETWEEN -100 AND 100),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_rebalance_config_asset UNIQUE (asset_id)
);
```

### Table: `portfolio.rebalance_plan`

One row per generated plan. `plan_json` holds the full multi-day correction schedule.

```sql
CREATE TABLE portfolio.rebalance_plan (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_date           DATE NOT NULL DEFAULT CURRENT_DATE,
    target_completion_date DATE NOT NULL,
    status                 VARCHAR(20) NOT NULL DEFAULT 'draft'
                               CHECK (status IN ('draft','active','completed','cancelled')),
    plan_json              JSONB NOT NULL DEFAULT '{}',
    email_sent             BOOLEAN NOT NULL DEFAULT FALSE,
    created_timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_timestamp      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `plan_json` structure

```json
{
  "summary": "3-day correction — 2 assets outside threshold",
  "total_drift_pct": 6.4,
  "actions": [
    {
      "ticker": "AAPL",
      "current_weight_pct": 25.0,
      "target_weight_pct": 20.0,
      "drift_pct": 5.0,
      "action": "reduce",
      "daily_steps": [
        { "date": "2026-03-24", "target_weight_pct": 23.3 },
        { "date": "2026-03-25", "target_weight_pct": 21.7 },
        { "date": "2026-03-26", "target_weight_pct": 20.0 }
      ]
    }
  ]
}
```

### Verification

```bash
alembic upgrade head -c portfolio.ini
alembic current -c portfolio.ini   # should show 4400000000d9
```

---

## Day 2 — Backend

**Branch:** `feature/issue-X-rebalance-service`

### New directory layout

```
src/backend/services/rebalancing/
    __init__.py
    domain/
        __init__.py
        entities.py                       # RebalanceConfig, RebalancePlan dataclasses
    infrastructure/
        __init__.py
        repositories/
            __init__.py
            rebalance_config_repository.py
            rebalance_plan_repository.py
            repository_factory.py
    plan_generator.py                     # pure function, no DB
    service.py                            # RebalancingService
    rebalancing_service_builder.py

src/shared/notifications/
    __init__.py
    email.py                              # EmailClient (smtplib, stdlib only)

src/orchestration/prefect/
    flow_rebalance_plan.py
```

### Patterns to follow

| Component | Copy from |
|---|---|
| Domain entities | `src/backend/services/portfolio/domain/entities.py` |
| Repository base | `src/shared/repositories/base_table_repository.py` |
| Repository factory | `src/backend/services/portfolio/infrastructure/repositories/repository_factory.py` |
| Service class | `src/backend/services/portfolio/service.py` |
| Builder | `src/backend/services/portfolio/portfolio_service_builder.py` |
| Prefect flow | `src/orchestration/prefect/flow_t212_gold.py` |

### `plan_generator.py` — pure function

```python
def generate_plan(
    configs: list[RebalanceConfig],
    current_weights: dict[str, float],   # ticker -> actual_weight_pct
) -> RebalancePlan
```

Logic:

1. For each active config, compute `drift = actual_weight - target_weight`
2. Skip if `abs(drift) <= rebalance_threshold_pct`
3. Divide drift linearly over `correction_days`
4. `action` = "reduce" if drift > 0 else "increase"
5. `target_completion_date = today + correction_days`
6. Return populated `RebalancePlan`

No DB access — fully testable in isolation.

### `RebalancingService`

```python
class RebalancingService:
    def load_configs(self) -> list[RebalanceConfig]
        # reads portfolio.rebalance_config WHERE is_active = TRUE

    def load_current_weights(self) -> dict[str, float]
        # reads analytics.fact_valuation (latest date_id)
        # SQLModelClient + raw SQL pattern (same as dashboard query_repository.py)

    def generate_and_save_plan(self) -> None
        # load -> generate -> persist -> email -> mark email_sent

    def get_latest_plan(self) -> RebalancePlan | None

    def upsert_config(self, config: RebalanceConfig) -> None
        # upsert on asset_id unique key
```

### `EmailClient` (`src/shared/notifications/email.py`)

Python stdlib only — `smtplib` + `email.mime`. No new dependencies.

New env vars (add to `.env`):

```
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
NOTIFICATION_EMAIL=
```

### `flow_rebalance_plan.py`

```python
@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_generate_rebalance_plan():
    service = build_rebalancing_service()
    service.generate_and_save_plan()

@flow
def flow_rebalance_plan():
    task_generate_rebalance_plan()
```

Add to `prefect.yaml`:

```yaml
- name: rebalance_plan
  entrypoint: src/orchestration/prefect/flow_rebalance_plan.py:flow_rebalance_plan
  work_pool:
    name: asset-monitoring-pool
  schedules:
    - interval: 86400
      anchor_date: "2026-01-01T07:00:00Z"
```

### Verification

- Call `service.generate_and_save_plan()` manually — confirm row in `portfolio.rebalance_plan`
- Confirm email arrives
- `prefect deploy --all`

---

## Day 3 — Frontend

**Branch:** `feature/issue-X-rebalance-dashboard`

### New files

```
src/dashboard/pages/portfolio/components/organisms/rebalance_panel.py
src/dashboard/pages/portfolio/callbacks/rebalancing.py
```

### `rebalance_panel.py`

Collapsible left drawer, 280px wide. Per asset row:

```
Asset name
├── Target Weight    [====|====]  20%
├── Min / Max        [=|========] 5%   [========|=] 35%
├── Risk Tolerance   [====|====]  50
├── Correction Days  [==|======]  3d
└── Momentum Bias    [====|====]  0
```

Uses `dcc.Slider`. Footer: **Save Config** button + status text + **Generate Plan** button.
Below sliders: read-only latest plan summary rendered from `plan_json`.

### `portfolio_page.py` changes

Add collapsible drawer outside and to the left of the existing `workspace-split` div.
Toggle button (Font Awesome `fa-scale-balanced`) in the filter bar area.

New component IDs:

- `"rebalance-panel-collapse"` — `dbc.Collapse` wrapper
- `"rebalance-panel-toggle-btn"` — filter bar icon button
- `"rebalance-config-store"` — `dcc.Store` for loaded configs
- `"rebalance-panel-save-btn"` — save button
- `"rebalance-panel-generate-btn"` — generate plan button
- `"rebalance-panel-status"` — status text span
- `"rebalance-panel-plan-summary"` — plan display div
- `{"type": "rebalance-slider", "index": ticker}` — pattern-matched sliders

### `callbacks/rebalancing.py`

```python
# Load configs + plan on page load
@callback(Output("rebalance-config-store", "data"), Input("portfolio_page_location", "pathname"))

# Render panel from store data
@callback(Output("rebalance-panel-body", "children"), Input("rebalance-config-store", "data"))

# Save slider values to DB
@callback(Output("rebalance-panel-status", "children"),
          Input("rebalance-panel-save-btn", "n_clicks"),
          State({"type": "rebalance-slider", "index": ALL}, "value"), ...)

# Trigger plan generation on demand
@callback(Output("rebalance-panel-plan-summary", "children"),
          Input("rebalance-panel-generate-btn", "n_clicks"))

# Toggle panel open/close
@callback(Output("rebalance-panel-collapse", "is_open"),
          Input("rebalance-panel-toggle-btn", "n_clicks"),
          State("rebalance-panel-collapse", "is_open"))
```

Register in `src/dashboard/pages/portfolio/callbacks/__init__.py`.

CSS additions to `src/dashboard/assets/sidebar.css` using existing theme vars
(`--bg-sidebar`, `--text-primary`, `--border-split`). Smooth width transition.

### Verification

- Open dashboard → ⚖ toggle opens panel
- Adjust slider → Save → DB row updated
- Generate Plan → plan summary renders in panel
- Verify no duplicate `Output(...)` IDs against existing callbacks
