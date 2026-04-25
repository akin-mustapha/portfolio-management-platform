# Drawdown-Based Auto-Buy Script

Monitors watched assets against their 14-day rolling price high (precomputed in the gold layer) and places tranche-based market buy orders via the Trading212 API when drawdown thresholds are crossed.

## How it works

1. Reads `price_drawdown_pct_14d` from `analytics.fact_technical` for each asset in `watchlist.yaml`
2. Compares drawdown against each asset's tranche thresholds
3. Fires the **deepest untriggered tranche** once per threshold per trading day
4. Checks available cash from `staging.account` before every order
5. Runs at **09:45** and **14:30** London time, Mon–Fri only

## Setup

```bash
cd scripts/autobuy
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/investment_db
API_URL=https://live.trading212.com/api/v0/
API_TOKEN=your_api_token
SECRET_TOKEN=your_secret_token

# Optional — log orders but skip the actual API call
DRY_RUN=false
```

## Configure your watchlist

Edit `watchlist.yaml` to set your monthly cap, assets, and tranche thresholds:

```yaml
monthly_limit: 500.0  # combined GBP cap across all assets per calendar month

assets:
  - name: Vanguard S&P 500 (Dist)
    ticker: VUSAl          # must match Trading212 external_id exactly
    tranches:
      - drawdown_pct: 5.0  # buy when 5% below 14-day high
        order_value: 50.0  # GBP amount
      - drawdown_pct: 10.0
        order_value: 100.0
```

Monthly spend is persisted to `state.json` in the same directory and resets automatically on the 1st of each month. Delete `state.json` to manually reset mid-month.

## Run

**Start the scheduler** (runs at 09:45 and 14:30 London time):

```bash
python scheduler.py
```

**Run once immediately** (for testing — still respects `DRY_RUN`):

```bash
python scheduler.py --run-now
```

**Dry run** (logs what would be ordered, no API calls):

```bash
DRY_RUN=true python scheduler.py --run-now
```

## File structure

```
scripts/autobuy/
├── watchlist.yaml    # assets and tranche definitions — edit this
├── config.py         # loads watchlist + env vars
├── db.py             # DB queries (drawdown, cash)
├── t212_client.py    # Trading212 API wrapper
├── strategy.py       # tranche evaluation and order logic
├── scheduler.py      # schedule setup and market hours guard
└── requirements.txt
```

## Notes

- Tranche state resets at midnight London time. If the process restarts mid-day, the worst case is one duplicate buy per breached threshold.
- A ticker is skipped if `price_drawdown_pct_14d` is NULL (fewer than 14 days of gold-layer data).
- The script reads cash from `staging.account`, which is populated by the hourly silver pipeline.
