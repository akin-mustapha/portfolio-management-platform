from dataclasses import dataclass

@dataclass
class Trading212Asset:
    external_id: int
    name: str
    description: str
    source_name = 'trading212'