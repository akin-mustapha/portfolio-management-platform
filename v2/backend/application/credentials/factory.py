from backend.application.credentials.service import CredentialsService
from backend.infrastructure.credentials.repository import CredentialsRepository


def build_credentials_service() -> CredentialsService:
    return CredentialsService(CredentialsRepository())
