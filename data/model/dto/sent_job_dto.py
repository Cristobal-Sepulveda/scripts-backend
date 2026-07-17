from dataclasses import dataclass, asdict
from typing import Any
import datetime

@dataclass
class SentJobDTO:
    url: str
    cargo: str
    entidad: str
    region: str
    ciudad: str
    updated_at: datetime.datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SentJobDTO":
        return cls(
            url=data.get("url", ""),
            cargo=data.get("cargo", ""),
            entidad=data.get("entidad", ""),
            region=data.get("region", ""),
            ciudad=data.get("ciudad", ""),
            updated_at=data.get("updated_at")
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if d["updated_at"] is None:
            d.pop("updated_at")
        return d
