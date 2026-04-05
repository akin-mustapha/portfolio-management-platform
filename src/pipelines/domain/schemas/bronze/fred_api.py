from pydantic import BaseModel, ConfigDict


class FredObservationItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    date: str
    value: str  # numeric string or "." for missing


class FredObservationsResponse(BaseModel):
    """
    Structural contract for the FRED series/observations API response envelope.
    extra="allow" tolerates FRED adding new envelope fields without breaking the pipeline.
    Validation failure raises — aborts the bronze run per bronze-layer policy.
    """
    model_config = ConfigDict(extra="allow")

    observations: list[FredObservationItem]
