from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from legacy.dashboard.controllers.asset_profile_controller import AssetProfileController
from backend.application.portfolio.factory import build_portfolio_service
from api.serialization import date_response

router = APIRouter(tags=["tags"])


class AssignTagRequest(BaseModel):
    tag_id: int


@router.get("/tags")
def get_tags():
    """Return all active tags available in the system."""
    service = build_portfolio_service()
    tags = service.get_all_tags()
    return date_response(tags)


@router.put("/assets/{ticker}/tags")
def assign_tag_to_asset(ticker: str, body: AssignTagRequest):
    """Assign a tag to an asset by ticker."""
    result = AssetProfileController().assign_tag(
        ticker=ticker.upper(), tag_id=body.tag_id
    )
    if result.startswith("Error") or "not found" in result:
        raise HTTPException(status_code=400, detail=result)
    return date_response({"status": result})
