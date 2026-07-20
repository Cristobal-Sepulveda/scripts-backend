from fastapi.testclient import TestClient
from main import app
from infrastructure.dependencies import get_job_repository, get_email_service
from infrastructure.middleware import verify_security_from_google_cloud_scheduler_task
from domain.repositories.job_repository import JobRepository
from domain.services.email_service import EmailService
from domain.entities.job import Job
from unittest.mock import MagicMock
import datetime
import pytest

mock_repo = MagicMock(spec=JobRepository)
mock_email = MagicMock(spec=EmailService)

app.dependency_overrides[get_job_repository] = lambda: mock_repo
app.dependency_overrides[get_email_service] = lambda: mock_email
app.dependency_overrides[verify_security_from_google_cloud_scheduler_task] = lambda: True

client = TestClient(app)

def test_run_kinesiologia_endpoint_success():
    # Arrange
    mock_repo.fetch_all_active_jobs.return_value = [
        {
            "Cargo": "Kinesiólogo",
            "Institución / Entidad": "Hospital",
            "Región": "Metropolitana",
            "Ciudad": "Santiago",
            "url": "http://example.com/kine"
        }
    ]
    mock_repo.get_sent_job_by_url.return_value = False
    mock_email.get_sender_email.return_value = "sender@example.com"
    mock_email.send_email.return_value = True

    # Act
    response = client.get("/scripts/run-job-finder/kinesiologia")

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_run_matroneria_endpoint_success():
    # Arrange
    mock_repo.fetch_all_active_jobs.return_value = [
        {
            "Cargo": "Matrona",
            "Institución / Entidad": "Hospital",
            "Región": "Metropolitana",
            "Ciudad": "Santiago",
            "url": "http://example.com/matron"
        }
    ]
    mock_repo.get_sent_job_by_url.return_value = False
    mock_email.get_sender_email.return_value = "sender@example.com"
    mock_email.send_email.return_value = True

    # Act
    response = client.get("/scripts/run-job-finder/matroneria")

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_run_cleanup_endpoint_success():
    # Arrange
    mock_repo.fetch_all_sent_jobs.return_value = [
        Job(
            cargo="Cargo",
            url="http://example.com/expired",
            entidad="Entidad",
            region="Region",
            ciudad="Ciudad",
            updated_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=40)
        )
    ]

    # Act
    response = client.get("/scripts/run-job-finder/cleanup")

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"
