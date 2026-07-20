from unittest.mock import MagicMock
import pytest
from data.repositories.job_repository_impl import JobRepositoryImpl
from domain.entities.job import Job

def test_get_sent_job_by_url_exists():
    # Arrange
    db = MagicMock()
    mock_query = MagicMock()
    mock_query.get.return_value = [MagicMock()]
    db.collection.return_value.where.return_value = mock_query
    repo = JobRepositoryImpl(db)

    # Act
    result = repo.get_sent_job_by_url("http://example.com")

    # Assert
    assert result is True
    db.collection.assert_called_once_with("sent_jobs")
    db.collection.return_value.where.assert_called_once_with(
        field_path="url",
        op_string="==",
        value="http://example.com"
    )

def test_get_sent_job_by_url_not_exists():
    # Arrange
    db = MagicMock()
    mock_query = MagicMock()
    mock_query.get.return_value = []
    db.collection.return_value.where.return_value = mock_query
    repo = JobRepositoryImpl(db)

    # Act
    result = repo.get_sent_job_by_url("http://example.com")

    # Assert
    assert result is False

def test_save_job():
    # Arrange
    db = MagicMock()
    mock_doc = MagicMock()
    db.collection.return_value.document.return_value = mock_doc
    repo = JobRepositoryImpl(db)
    job = Job(
        cargo="Kinesiología",
        url="http://example.com",
        entidad="Hospital",
        region="Metropolitana",
        ciudad="Santiago",
        updated_at=None
    )

    # Act
    repo.save_job(job)

    # Assert
    db.collection.assert_called_once_with("sent_jobs")
    mock_doc.set.assert_called_once()

def test_fetch_all_sent_jobs():
    # Arrange
    db = MagicMock()
    mock_doc1 = MagicMock()
    mock_doc1.to_dict.return_value = {
        "url": "http://example.com/1",
        "cargo": "Cargo 1",
        "entidad": "Entidad 1",
        "region": "Region 1",
        "ciudad": "Ciudad 1",
        "updated_at": None
    }
    db.collection.return_value.stream.return_value = [mock_doc1]
    repo = JobRepositoryImpl(db)

    # Act
    jobs = repo.fetch_all_sent_jobs()

    # Assert
    assert len(jobs) == 1
    assert jobs[0].url == "http://example.com/1"
    assert jobs[0].cargo == "Cargo 1"

def test_delete_job_by_url():
    # Arrange
    db = MagicMock()
    mock_doc1 = MagicMock()
    mock_doc1.id = "doc123"
    mock_query = MagicMock()
    mock_query.get.return_value = [mock_doc1]
    db.collection.return_value.where.return_value = mock_query
    
    mock_doc_ref = MagicMock()
    db.collection.return_value.document.return_value = mock_doc_ref
    
    repo = JobRepositoryImpl(db)

    # Act
    repo.delete_job_by_url("http://example.com")

    # Assert
    db.collection.return_value.document.assert_called_once_with("doc123")
    mock_doc_ref.delete.assert_called_once()
