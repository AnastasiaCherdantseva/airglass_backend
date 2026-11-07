from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UnitOutput:
    id: UUID
    name: str
    symbol: str
