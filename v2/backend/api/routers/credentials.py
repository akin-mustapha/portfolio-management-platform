from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.application.credentials.service import build_credentials_service
from backend.api.serialization import date_response

router = APIRouter(tags=["credentials"])

PROVIDER = "trading212"


class CredentialsRequest(BaseModel):
    api_key: str
    secret_token: str = ""
    api_url: str = ""


@router.get("/credentials")
def get_credentials():
    """Return stored API credentials for the default provider."""
    try:
        return date_response(build_credentials_service().get(PROVIDER))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credentials")
def save_credentials(body: CredentialsRequest):
    """Persist API credentials for the default provider."""
    try:
        build_credentials_service().save(
            PROVIDER, body.api_key, body.secret_token, body.api_url
        )
        return date_response({"status": "saved"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
