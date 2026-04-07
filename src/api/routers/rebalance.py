from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.application.rebalancing.service import RebalancingService
from backend.domain.rebalancing.entities import RebalanceConfig
from backend.domain.rebalancing.value_objects import WeightBand, RebalanceThreshold
from api.serialization import date_response

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


@router.get("/rebalance/configs")
def get_rebalance_configs():
    """Return all active rebalance configs with their tickers."""
    service = RebalancingService()
    configs = service.load_configs()
    return date_response(
        [
            {
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
            for c in configs
        ]
    )


@router.post("/rebalance/configs")
def save_rebalance_config(body: RebalanceConfigRequest):
    """Create or update a rebalance config for an asset (upsert on asset_id)."""
    service = RebalancingService()
    config = RebalanceConfig(
        id=None,
        asset_id=body.asset_id,
        ticker=body.ticker,
        weight_band=WeightBand(
            target=body.target_weight_pct,
            min=body.min_weight_pct,
            max=body.max_weight_pct,
        ),
        rebalance_threshold=RebalanceThreshold(body.rebalance_threshold_pct),
        correction_days=body.correction_days,
        is_active=body.is_active,
    )
    try:
        service.upsert_config(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return date_response({"status": "saved"})


@router.post("/rebalance/plan")
def generate_rebalance_plan():
    """Generate (and persist) a rebalancing plan based on current configs."""
    service = RebalancingService()
    try:
        plan = service.generate_and_save_plan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if plan is None:
        return date_response({"status": "no_drift", "plan": None})

    return date_response({"status": "generated", "plan": plan.to_record()})
