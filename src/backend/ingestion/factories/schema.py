from ..domain.schemas.bronze.account_api import AccountAPIResponse
from ..domain.schemas.bronze.asset_api import AssetAPIRecord

class Schema:
  _registry = {
    "account_data": AccountAPIResponse,
    "position_data": AssetAPIRecord,
  }
  @classmethod
  def get(self, name: str):
    return self._registry.get(name.lower())