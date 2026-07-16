from domain.repositories.job_repository import JobRepository

class CleanupInactiveJobsUseCase:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    def execute(self) -> None:
        all_items = self.job_repository.fetch_all_active_jobs()
        if not all_items:
            return

        active_urls = {
            item.get("url") or item.get("URL")
            for item in all_items
            if item.get("url") or item.get("URL")
        }
        self.job_repository.cleanup_inactive_jobs(active_urls)
