from dataclasses import dataclass


@dataclass(frozen=True)
class ApiKey:
    value: str

    def __post_init__(self):
        stripped = self.value.strip()
        if not stripped:
            raise ValueError("api_key is required")
        object.__setattr__(self, "value", stripped)

    def __str__(self) -> str:
        return self.value
