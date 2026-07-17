from dataclasses import dataclass
import datetime
import hashlib

@dataclass
class Job:
    cargo: str
    url: str
    entidad: str
    region: str
    ciudad: str
    updated_at: datetime.datetime | None = None

    @property
    def doc_id(self) -> str:
        return hashlib.sha256(self.url.encode("utf-8")).hexdigest()
