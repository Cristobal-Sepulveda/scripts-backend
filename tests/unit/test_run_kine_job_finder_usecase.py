from unittest.mock import MagicMock
import pytest
from domain.usecases.run_kine_job_finder_usecase import RunKineJobFinderUseCase
from domain.repositories.job_repository import JobRepository
from domain.services.email_service import EmailService
from domain.exceptions.domain_exception import EmailDispatchError

def test_execute_no_active_jobs():
    # given
    repo = MagicMock(spec=JobRepository)
    repo.fetch_all_active_jobs.return_value = []
    email = MagicMock(spec=EmailService)
    usecase = RunKineJobFinderUseCase(job_repository=repo, email_service=email)

    # when
    usecase.execute()

    # then
    repo.fetch_all_active_jobs.assert_called_once()
    repo.get_sent_job_by_url.assert_not_called()
    email.send_email.assert_not_called()

def test_execute_no_matching_jobs():
    # given
    repo = MagicMock(spec=JobRepository)
    repo.fetch_all_active_jobs.return_value = [
        {
            "Cargo": "Ingeniero Civil",
            "Institución / Entidad": "MOP",
            "Región": "Metropolitana",
            "Ciudad": "Santiago",
            "url": "http://example.com/1"
        }
    ]
    email = MagicMock(spec=EmailService)
    usecase = RunKineJobFinderUseCase(job_repository=repo, email_service=email)

    # when
    usecase.execute()

    # then
    repo.fetch_all_active_jobs.assert_called_once()
    repo.get_sent_job_by_url.assert_not_called()
    email.send_email.assert_not_called()

def test_execute_already_sent_jobs():
    # given
    repo = MagicMock(spec=JobRepository)
    repo.fetch_all_active_jobs.return_value = [
        {
            "Cargo": "Kinesiólogo",
            "Institución / Entidad": "Hospital",
            "Región": "Metropolitana",
            "Ciudad": "Santiago",
            "url": "http://example.com/kine"
        }
    ]
    repo.get_sent_job_by_url.return_value = True
    email = MagicMock(spec=EmailService)
    usecase = RunKineJobFinderUseCase(job_repository=repo, email_service=email)

    # when
    usecase.execute()

    # then
    repo.get_sent_job_by_url.assert_called_once_with("http://example.com/kine")
    repo.save_job.assert_not_called()
    email.send_email.assert_not_called()

def test_execute_send_success():
    # given
    repo = MagicMock(spec=JobRepository)
    repo.fetch_all_active_jobs.return_value = [
        {
            "Cargo": "Kinesiólogo",
            "Institución / Entidad": "Hospital",
            "Región": "Metropolitana",
            "Ciudad": "Santiago",
            "url": "http://example.com/kine"
        }
    ]
    repo.get_sent_job_by_url.return_value = False
    email = MagicMock(spec=EmailService)
    email.get_sender_email.return_value = "sender@example.com"
    email.send_email.return_value = True
    usecase = RunKineJobFinderUseCase(job_repository=repo, email_service=email)

    # when
    usecase.execute()

    # then
    repo.save_job.assert_called_once()
    email.send_email.assert_called_once()

def test_execute_send_email_error():
    # given
    repo = MagicMock(spec=JobRepository)
    repo.fetch_all_active_jobs.return_value = [
        {
            "Cargo": "Kinesiólogo",
            "Institución / Entidad": "Hospital",
            "Región": "Metropolitana",
            "Ciudad": "Santiago",
            "url": "http://example.com/kine"
        }
    ]
    repo.get_sent_job_by_url.return_value = False
    email = MagicMock(spec=EmailService)
    email.get_sender_email.return_value = "sender@example.com"
    email.send_email.return_value = False
    usecase = RunKineJobFinderUseCase(job_repository=repo, email_service=email)

    # when / then
    with pytest.raises(EmailDispatchError):
        usecase.execute()
