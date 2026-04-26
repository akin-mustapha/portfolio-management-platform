from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.infrastructure.credentials.repository import CredentialsRepository
from api.serialization import date_response

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
        repo = CredentialsRepository()
        row = repo.load(PROVIDER)
        if row:
            return date_response(
                {
                    "api_key": row.get("api_key", ""),
                    "secret_token": row.get("secret_token", ""),
                    "api_url": row.get("api_url", ""),
                }
            )
        return date_response({"api_key": "", "secret_token": "", "api_url": ""})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credentials")
def save_credentials(body: CredentialsRequest):
    """Persist API credentials for the default provider."""
    api_key = body.api_key.strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key is required")
    try:
        CredentialsRepository().save(
            PROVIDER,
            api_key,
            body.secret_token.strip(),
            body.api_url.strip(),
        )
        return date_response({"status": "saved"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
