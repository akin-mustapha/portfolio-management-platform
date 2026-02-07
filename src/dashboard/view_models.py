from dataclasses import dataclass

@dataclass
class PortfolioViewModel:
    name: str
    value: float
    change: float