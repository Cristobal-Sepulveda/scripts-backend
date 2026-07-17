from abc import ABC, abstractmethod
from domain.entities.job import Job

class JobRepository(ABC):
    @abstractmethod
    def fetch_all_active_jobs(self) -> list[dict]:
        pass
    
    @abstractmethod
    def get_sent_job_by_url(self, url: str) -> bool:
        pass

    @abstractmethod
    def save_job(self, job: Job) -> None:
        pass
