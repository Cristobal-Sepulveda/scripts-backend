from google.cloud import firestore
from fastapi import Depends

from domain.usecases.run_kine_job_finder_usecase import RunKineJobFinderUseCase
from domain.usecases.run_matron_job_finder_usecase import RunMatronJobFinderUseCase
from domain.usecases.cleanup_inactive_jobs_usecase import CleanupInactiveJobsUseCase
from domain.repositories.job_repository import JobRepository
from domain.services.email_service import EmailService
from data.repositories.firestore_job_repository import JobRepositoryImpl
from data.network.gmail_email_service import GmailEmailService

db_client = firestore.Client()

def get_db() -> firestore.Client:
    return db_client

def get_job_repository(db: firestore.Client = Depends(get_db)) -> JobRepository:
    return JobRepositoryImpl(db=db)

def get_email_service() -> EmailService:
    return GmailEmailService()

def get_run_kine_job_finder_usecase(
    job_repository: JobRepository = Depends(get_job_repository),
    email_service: EmailService = Depends(get_email_service)
) -> RunKineJobFinderUseCase:
    return RunKineJobFinderUseCase(
        job_repository=job_repository,
        email_service=email_service
    )

def get_run_matron_job_finder_usecase(
    job_repository: JobRepository = Depends(get_job_repository),
    email_service: EmailService = Depends(get_email_service)
) -> RunMatronJobFinderUseCase:
    return RunMatronJobFinderUseCase(
        job_repository=job_repository,
        email_service=email_service
    )

def get_cleanup_inactive_jobs_usecase(
    job_repository: JobRepository = Depends(get_job_repository)
) -> CleanupInactiveJobsUseCase:
    return CleanupInactiveJobsUseCase(job_repository=job_repository)


