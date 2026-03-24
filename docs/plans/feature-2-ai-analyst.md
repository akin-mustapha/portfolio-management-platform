# Feature 2 — AI Portfolio Analyst

## Context

Adds a daily AI-generated portfolio brief. The system reads the gold layer, formats a snapshot, calls the Claude API, and returns a structured brief (findings, risk flags, suggested actions). The brief is emailed daily and displayed in a new "Insights" tab on the dashboard. Read-only, advisory only.

Depends on: Feature 1 (reuses `EmailClient` from `src/shared/notifications/email.py`).

## Branching

| Branch | Layer | Merges before |
|---|---|---|
| `feature/issue-X-ai-analyst-schema` | Storage | — |
| `feature/issue-X-ai-analyst-service` | Backend | schema merged |
| `feature/issue-X-ai-analyst-dashboard` | Dashboard + Orchestration | service merged |

---

## Day 1 — Database

**New file:** `migrations/postgres/versions/portfolio/010_ai_brief_table.py`

```
revision:      4400000000da
down_revision: 4400000000d9
```

### Table: `portfolio.ai_brief`

```sql
CREATE TABLE portfolio.ai_brief (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    brief_json        JSONB NOT NULL DEFAULT '{}',
    email_sent        BOOLEAN NOT NULL DEFAULT FALSE,
    created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `brief_json` structure

```json
{
  "snapshot_timestamp": "2026-03-23T07:00:00Z",
  "summary": "Portfolio is 4.2% below last month's peak...",
  "findings": [
    { "ticker": "AAPL", "finding": "Down 18% from ATH, elevated 30d volatility" }
  ],
  "risk_flags": [
    { "ticker": "NVDA", "flag": "Position weight 28% — above comfortable range" }
  ],
  "suggested_actions": [
    { "ticker": "AAPL", "action": "DCA bias 0.82 — current price below avg cost, consider adding" }
  ]
}
```

### New dependency

Add to `requirements.txt`:

```
anthropic
```

### Verification

```bash
alembic upgrade head -c portfolio.ini
alembic current -c portfolio.ini   # should show 4400000000da
```

---

## Day 2 — Backend

**Branch:** `feature/issue-X-ai-analyst-service`

### New directory layout

```
src/backend/services/agent/
    __init__.py
    domain/
        __init__.py
        entities.py               # AgentBrief dataclass
    infrastructure/
        __init__.py
        repositories/
            __init__.py
            ai_brief_repository.py
            repository_factory.py
    snapshot.py                   # PortfolioSnapshot builder (reads analytics layer)
    claude_client.py              # ClaudeClient wrapping anthropic SDK
    service.py                    # PortfolioAgentService
    agent_service_builder.py

src/orchestration/prefect/
    flow_ai_analyst.py
```

### `snapshot.py` — `PortfolioSnapshot`

Reads from `analytics` schema using the same raw SQL + `SQLModelClient` pattern as
`src/dashboard/infrastructure/repositories/query_repository.py`.

Queries:

- `analytics.fact_portfolio_daily` — latest portfolio totals, cash, P&L
- `analytics.fact_valuation` — per-asset weight, unrealised P&L, cost basis
- `analytics.fact_technical` — per-asset drawdown, volatility, MA values
- `analytics.fact_signal` — per-asset DCA bias, MA crossover signals

Returns a compact, formatted context block — not raw query results.

### `claude_client.py` — `ClaudeClient`

```python
import anthropic

class ClaudeClient:
    MODEL = "claude-sonnet-4-6"

    def __init__(self):
        self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def analyse(self, snapshot_context: str) -> dict:
        # System prompt: defines role, explains available metrics,
        #   instructs Claude to return JSON matching AgentBrief schema
        # Returns parsed + Pydantic-validated AgentBrief dict
        # On JSON parse failure: retry once, then fallback to {"summary": raw_text}
```

New env var: `ANTHROPIC_API_KEY=`

### `PortfolioAgentService`

```python
class PortfolioAgentService:
    def generate_and_save_brief(self) -> None
        # 1. PortfolioSnapshot.build()
        # 2. ClaudeClient().analyse(snapshot)
        # 3. Validate with Pydantic
        # 4. Persist to portfolio.ai_brief
        # 5. EmailClient().send(subject, body)
        # 6. Mark email_sent = TRUE

    def get_latest_brief(self) -> AgentBrief | None
```

Reuses `EmailClient` from `src/shared/notifications/email.py` (built in Feature 1).

### `flow_ai_analyst.py`

```python
@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_generate_ai_brief():
    service = build_agent_service()
    service.generate_and_save_brief()

@flow
def flow_ai_analyst():
    task_generate_ai_brief()
```

Add to `prefect.yaml`:

```yaml
- name: ai_analyst
  entrypoint: src/orchestration/prefect/flow_ai_analyst.py:flow_ai_analyst
  work_pool:
    name: asset-monitoring-pool
  schedules:
    - interval: 86400
      anchor_date: "2026-01-01T08:00:00Z"
```

### Verification

- Call `service.generate_and_save_brief()` manually
- Confirm row in `portfolio.ai_brief` with valid JSON
- Confirm email arrives
- `prefect deploy --all`

---

## Day 3 — Frontend

**Branch:** `feature/issue-X-ai-analyst-dashboard`

### New files

```
src/dashboard/pages/portfolio/tabs/tab_insights.py
src/dashboard/pages/portfolio/callbacks/insights.py
```

### New tab in `workspace_tabs.py`

Add a new `dbc.Tab` following the existing pattern:

```python
dbc.Tab(
    label="Insights",
    tab_id="tab-insights",
    tab_class_name="workspace-tab",
    active_tab_class_name="workspace-tab--active",
    children=tab_insights_content(),
)
```

### `tab_insights.py` — layout

```
[ AI Brief — last updated: 23 Mar 2026 07:00 ]   [ Refresh ]

Summary
  "Portfolio is 4.2% below last month's peak..."

Risk Flags
  ⚠ NVDA — Position weight 28% above comfortable range

Suggested Actions
  → AAPL — DCA bias 0.82, consider adding

Findings
  • AAPL — Down 18% from ATH, elevated 30d volatility
  • ...
```

Static layout — no charts, plain text + structured sections.
Uses `html.Div`, `html.P`, `html.Ul`/`html.Li`. Styled with existing theme variables.

### `callbacks/insights.py`

```python
# Load latest brief on tab activation
@callback(
    Output("insights-brief-content", "children"),
    Output("insights-last-updated", "children"),
    Input("workspace-tabs", "active_tab"),
)
def load_brief(active_tab):
    if active_tab != "tab-insights":
        raise PreventUpdate
    # fetch latest portfolio.ai_brief row, render sections

# Refresh on button click
@callback(
    Output("insights-brief-content", "children", allow_duplicate=True),
    Input("insights-refresh-btn", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_brief(n_clicks):
    # call service.generate_and_save_brief(), re-fetch and render
```

Register in `src/dashboard/pages/portfolio/callbacks/__init__.py`.

### Verification

- Click "Insights" tab — brief renders
- Click Refresh — new brief generated and displayed
- Confirm snapshot timestamp shown, not stale
- Verify no duplicate `Output(...)` IDs
