from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.application.rebalancing.factory import build_rebalancing_service
from backend.domain.rebalancing.entities import RebalanceConfig
from backend.api.serialization import date_response

router = APIRouter(tags=["rebalance"])


class RebalanceConfigRequest(BaseModel):
    asset_id: str
    ticker: str
    target_weight_pct: float
    min_weight_pct: float
    max_weight_pct: float
    rebalance_threshold_pct: float = 5.0
    correction_days: int = 5
    is_active: bool = True


def _serialize_config(c: RebalanceConfig) -> dict:
    return {
        "id": c.id,
        "asset_id": c.asset_id,
        "ticker": c.ticker,
        "target_weight_pct": c.target_weight_pct,
        "min_weight_pct": c.min_weight_pct,
        "max_weight_pct": c.max_weight_pct,
        "rebalance_threshold_pct": c.rebalance_threshold_pct,
        "correction_days": c.correction_days,
        "is_active": c.is_active,
    }


@router.get("/rebalance/configs")
def get_rebalance_configs():
    """Return all active rebalance configs with their tickers."""
    svc = build_rebalancing_service()
    configs = svc.load_configs()
    return date_response([_serialize_config(c) for c in configs])


@router.post("/rebalance/configs")
def save_rebalance_config(body: RebalanceConfigRequest):
    """Create or update a rebalance config for an asset (upsert on asset_id)."""
    svc = build_rebalancing_service()
    config = svc.create_config(**body.model_dump())
    try:
        svc.upsert_config(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return date_response({"status": "saved"})


@router.post("/rebalance/plan")
def generate_rebalance_plan():
    """Generate (and persist) a rebalancing plan based on current configs."""
    svc = build_rebalancing_service()
    try:
        plan = svc.generate_and_save_plan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if plan is None:
        return date_response({"status": "no_drift", "plan": None})

    return date_response({"status": "generated", "plan": plan.to_record()})
