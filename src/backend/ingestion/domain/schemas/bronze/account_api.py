from pydantic import BaseModel, ConfigDict


class AccountCash(BaseModel):
    model_config = ConfigDict(extra='allow')
    inPies: float
    availableToTrade: float
    reservedForOrders: float


class AccountInvestments(BaseModel):
    model_config = ConfigDict(extra='allow')
    totalCost: float
    realizedProfitLoss: float
    unrealizedProfitLoss: float


class AccountAPIResponse(BaseModel):
    """
    Structural contract for the Trading212 equity/account/summary API response.
    Checks that required fields are present — extra fields are allowed to
    avoid breaking on new API additions. Used in the bronze pipeline only.
    """
    model_config = ConfigDict(extra='allow')
    id: int
    cash: AccountCash
    currency: str
    totalValue: float
    investments: AccountInvestments
