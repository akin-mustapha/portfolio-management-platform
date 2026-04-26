from pydantic import BaseModel, ConfigDict


class AssetInstrument(BaseModel):
    model_config = ConfigDict(extra="allow")
    ticker: str
    name: str
    isin: str
    currency: str


class AssetWalletImpact(BaseModel):
    model_config = ConfigDict(extra="allow")
    currency: str
    totalCost: float
    currentValue: float
    unrealizedProfitLoss: float
    fxImpact: float | None = None


class AssetAPIRecord(BaseModel):
    """
    Structural contract for the Trading212 equity/positions API response.
    Checks that required fields are present — extra fields are allowed to
    avoid breaking on new API additions. Used in the bronze pipeline only.
    """

    model_config = ConfigDict(extra="allow")
    instrument: AssetInstrument
    quantity: float
    currentPrice: float
    averagePricePaid: float
    walletImpact: AssetWalletImpact
    createdAt: str
    quantityAvailableForTrading: float | None = None
    quantityInPies: float | None = None
