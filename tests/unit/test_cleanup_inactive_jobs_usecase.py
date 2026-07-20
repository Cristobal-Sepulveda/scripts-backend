from unittest.mock import MagicMock
import pytest
import datetime
from domain.usecases.cleanup_inactive_jobs_usecase import CleanupInactiveJobsUseCase
from domain.repositories.job_repository import JobRepository
from domain.entities.job import Job

def test_cleanup_no_sent_jobs():
    # Arrange
    repo = MagicMock(spec=JobRepository)
    repo.fetch_all_sent_jobs.return_value = []
    usecase = CleanupInactiveJobsUseCase(repo)

    # Act
    usecase.execute()

    # Assert
    repo.fetch_all_sent_jobs.assert_called_once()
    repo.delete_job_by_url.assert_not_called()

def test_cleanup_deletes_expired_jobs():
    # Arrange
    repo = MagicMock(spec=JobRepository)
    now = datetime.datetime.now(datetime.timezone.utc)
    expired_date = now - datetime.timedelta(days=31)
    fresh_date = now - datetime.timedelta(days=10)

    job1 = Job(
        cargo="Kinesiología",
        url="http://example.com/expired",
        entidad="Hospital",
        region="Metropolitana",
        ciudad="Santiago",
        updated_at=expired_date
    )
    job2 = Job(
        cargo="Matrona",
        url="http://example.com/fresh",
        entidad="Hospital",
        region="Metropolitana",
        ciudad="Santiago",
        updated_at=fresh_date
    )

    repo.fetch_all_sent_jobs.return_value = [job1, job2]
    usecase = CleanupInactiveJobsUseCase(repo)

    # Act
    usecase.execute()

    # Assert
    repo.delete_job_by_url.assert_called_once_with("http://example.com/expired")
