from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.application.portfolio.factory import build_portfolio_service
from backend.api.serialization import date_response

router = APIRouter(tags=["tags"])


class AssignTagRequest(BaseModel):
    tag_id: int


@router.get("/tags")
def get_tags():
    """Return all active tags available in the system."""
    tags = build_portfolio_service().get_all_tags()
    return date_response(tags)


@router.put("/assets/{ticker}/tags")
def assign_tag_to_asset(ticker: str, body: AssignTagRequest):
    """Assign a tag to an asset by ticker."""
    try:
        build_portfolio_service().assign_tag(ticker.upper(), body.tag_id)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return date_response({"status": "Tag assigned."})
