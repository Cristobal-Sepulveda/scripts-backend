from abc import ABC, abstractmethod
from typing import Pattern
from domain.entities.job import Job

class JobDataSource(ABC):
    @abstractmethod
    def fetch_all_active_jobs(self) -> list[dict]:
        pass

    @abstractmethod
    def filter_jobs(self, items: list[dict], pattern: Pattern) -> list[Job]:
        pass
