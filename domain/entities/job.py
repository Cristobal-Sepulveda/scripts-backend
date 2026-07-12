from dataclasses import dataclass
import hashlib

@dataclass
class Job:
    cargo: str
    url: str
    entidad: str
    region: str
    ciudad: str
    times_sent: int = 0
    active: bool = True

    @property
    def doc_id(self) -> str:
        return hashlib.sha256(self.url.encode("utf-8")).hexdigest()

    @property
    def can_be_sent(self) -> bool:
        return self.times_sent < 2
