# FRED API Integration

**Source:** Federal Reserve Economic Data (FRED), maintained by the Federal Reserve Bank of St. Louis.
**Base URL:** `https://api.stlouisfed.org/fred/`
**API Key:** Free registration at `https://fred.stlouisfed.org/docs/api/api_key.html`
**Docs:** `https://fred.stlouisfed.org/docs/api/fred/`

---

## Why This Project Uses FRED

FRED provides the external reference data needed to compute metrics that cannot be derived from the Trading212 pipeline alone. Two metrics in `docs/02-architecture/design/metrics-reference.md` are blocked on FRED data:

| Metric | FRED Data Needed |
|---|---|
| **Sharpe Ratio** | Risk-free rate (3-month T-Bill or UK Gilt yield) |
| **Beta** | Market index daily returns (S&P 500 or equivalent) |

---

## Series in Use

| Series ID | Name | Frequency | Used For |
|---|---|---|---|
| `DTB3` | 3-Month Treasury Bill: Secondary Market Rate | Daily | Risk-free rate for Sharpe Ratio |
| `SP500` | S&P 500 | Daily | Benchmark for Beta computation |

---

## Candidate Series (Not Yet Implemented)

These series are relevant to future dashboard questions but have no active pipeline yet. Do not add them until a specific dashboard question requires them.

| Series ID | Name | Frequency | Potential Use |
|---|---|---|---|
| `DGS10` | 10-Year Treasury Constant Maturity Rate | Daily | Longer-term risk-free rate alternative |
| `VIXCLS` | CBOE Volatility Index (VIX) | Daily | Market fear/volatility context widget |
| `T10YIE` | 10-Year Breakeven Inflation Rate | Daily | Real return context |
| `DEXUSUK` | US Dollar to UK Pound Sterling Exchange Rate | Daily | FX macro context for UK-denominated portfolio |
| `CPIAUCSL` | Consumer Price Index (All Urban Consumers) | Monthly | Inflation-adjusted return context |
| `IRLTLT01GBM156N` | UK 10-Year Government Bond Yield | Monthly | UK-specific risk-free rate alternative |

---

## Data Access Pattern

FRED serves time series via a REST API. The standard request pattern for a daily series:

```
GET https://api.stlouisfed.org/fred/series/observations
  ?series_id=DTB3
  &observation_start=2020-01-01
  &file_type=json
  &api_key=<YOUR_KEY>
```

Response is a JSON array of `{ date, value }` observations. Missing values are returned as `"."` and must be forward-filled or dropped before use.

---

## Storage

FRED data belongs in the `raw` schema on arrival (append-only, partitioned by ingest date), then normalised to `staging` before being joined with pipeline data for gold layer metric computation.

No FRED tables exist yet. Schema design should follow the existing medallion pattern documented in `docs/02-architecture/design/schema/`.

---

## Update Frequency

Most FRED daily series are published within 1 business day of the reference date. The risk-free rate (`DTB3`) and market index (`SP500`) are sufficient to update on a daily schedule, aligned with the existing `flow_t212_gold` cadence.
