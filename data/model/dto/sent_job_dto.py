from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class SentJobDTO:
    url: str
    cargo: str
    entidad: str
    region: str
    ciudad: str
    times_sent: int
    active: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SentJobDTO":
        return cls(
            url=data.get("url", ""),
            cargo=data.get("cargo", ""),
            entidad=data.get("entidad", ""),
            region=data.get("region", ""),
            ciudad=data.get("ciudad", ""),
            times_sent=data.get("times_sent", 0),
            active=data.get("active", True)
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
