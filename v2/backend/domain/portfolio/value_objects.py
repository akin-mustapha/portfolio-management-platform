from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Ticker:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Ticker must be non-empty")
        object.__setattr__(self, "value", self.value.upper())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Currency:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Currency must be non-empty")
        if len(self.value) != 3:
            raise ValueError("Currency must be 3 characters (ISO 4217)")
        object.__setattr__(self, "value", self.value.upper())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TrendSignal:
    value: str

    def __post_init__(self):
        if self.value not in ("Bullish", "Bearish"):
            raise ValueError(
                f"TrendSignal must be 'Bullish' or 'Bearish', got '{self.value}'"
            )

    @classmethod
    def from_ma_crossover(cls, signal: float | None) -> TrendSignal:
        return cls("Bullish" if (signal or 0) > 0 else "Bearish")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Broker:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Broker must be non-empty")

    def __str__(self) -> str:
        return self.value
