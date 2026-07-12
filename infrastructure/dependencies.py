from google.cloud import firestore
from fastapi import Depends

from domain.usecases.run_job_finder_usecase import RunJobFinderUseCase
from domain.repositories.job_repository import JobRepository
from domain.services.email_service import EmailService
from domain.repositories.job_datasource import JobDataSource
from data.repositories.firestore_job_repository import FirestoreJobRepository
from data.services.gmail_email_service import GmailEmailService
from data.network.portal_client import PortalClient

db_client = firestore.Client()

def get_db() -> firestore.Client:
    return db_client

def get_job_repository(db: firestore.Client = Depends(get_db)) -> JobRepository:
    return FirestoreJobRepository(db=db)

def get_email_service() -> EmailService:
    return GmailEmailService()

def get_portal_client() -> JobDataSource:
    return PortalClient()

def get_run_job_finder_usecase(
    job_repository: JobRepository = Depends(get_job_repository),
    email_service: EmailService = Depends(get_email_service),
    portal_client: JobDataSource = Depends(get_portal_client)
) -> RunJobFinderUseCase:
    return RunJobFinderUseCase(
        job_repository=job_repository,
        email_service=email_service,
        portal_client=portal_client
    )
