from abc import ABC, abstractmethod
from domain.entities.job import Job

class JobRepository(ABC):
    @abstractmethod
    def fetch_all_active_jobs(self) -> list[dict]:
        pass
    
    @abstractmethod
    def get_sent_job_by_url(self, url: str) -> Job | None:
        pass

    @abstractmethod
    def increment_sent_count(self, jobs: list[Job]) -> None:
        pass

    @abstractmethod
    def cleanup_inactive_jobs(self, active_urls: set[str]) -> None:
        pass
