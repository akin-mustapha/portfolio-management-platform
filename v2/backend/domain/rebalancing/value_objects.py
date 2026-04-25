from dataclasses import dataclass


@dataclass(frozen=True)
class WeightBand:
    target: float
    min: float
    max: float

    def __post_init__(self):
        for val in (self.target, self.min, self.max):
            if not (0.0 <= val <= 100.0):
                raise ValueError(
                    f"WeightBand values must be in [0.0, 100.0], got {val}"
                )
        if not (self.min <= self.target <= self.max):
            raise ValueError(
                f"WeightBand invariant violated: min={self.min} <= target={self.target} <= max={self.max}"
            )


@dataclass(frozen=True)
class RebalanceThreshold:
    value: float

    def __post_init__(self):
        if self.value <= 0.0:
            raise ValueError(f"RebalanceThreshold must be > 0.0, got {self.value}")


@dataclass(frozen=True)
class PlanStatus:
    _VALID = frozenset({"pending", "active", "completed", "cancelled", "draft"})

    value: str

    def __post_init__(self):
        if self.value not in self._VALID:
            raise ValueError(
                f"PlanStatus must be one of {sorted(self._VALID)}, got '{self.value}'"
            )

    def __str__(self) -> str:
        return self.value
