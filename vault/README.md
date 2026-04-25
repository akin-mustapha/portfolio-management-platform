# Portfolio Management Platform — v2

All commands are run from the `v2/` directory.

---

## FastAPI server

```bash
uvicorn backend.api.main:app --reload --port 8001
```

---

## Prefect

**Deploy all flows:**

```bash
prefect deploy --all
```

**Run a flow directly:**

```bash
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

## Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev       # dev server on :5173
npm run build     # production build → frontend/dist/
```
