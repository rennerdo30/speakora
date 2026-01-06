import pytest
from fastapi.testclient import TestClient
from tool.api import create_app
from tool.config import Config
from unittest.mock import patch, MagicMock

@pytest.fixture
def client(test_config):
    app = create_app(test_config)
    return TestClient(app)

def test_list_jobs_empty(client):
    with patch("tool.api.JobQueue.list_jobs", return_value=[]):
        response = client.get("/api/jobs")
        assert response.status_code == 200
        assert response.json() == []

def test_create_job(client):
    with patch("tool.api.JobQueue.enqueue", return_value="job_123"):
        response = client.post("/api/jobs?input_file=test.wav&target_lang=deu")
        assert response.status_code == 200
        assert response.json() == {"job_id": "job_123"}

def test_get_job(client):
    mock_job = MagicMock()
    mock_job.id = "job_123"
    mock_job.status = "queued"
    
    with patch("tool.api.JobQueue.get_job", return_value=mock_job):
        response = client.get("/api/jobs/job_123")
        assert response.status_code == 200

def test_get_job_not_found(client):
    with patch("tool.api.JobQueue.get_job", return_value=None):
        response = client.get("/api/jobs/nonexistent")
        assert response.status_code == 404

def test_pause_resume(client):
    with patch("tool.api.JobQueue.update_job_status") as mock_update:
        response = client.patch("/api/jobs/job_123/pause")
        assert response.status_code == 200
        assert mock_update.called
        
        response = client.patch("/api/jobs/job_123/resume")
        assert response.status_code == 200
        assert mock_update.call_count == 2

def test_system_info(client):
    with patch("tool.device_manager.get_device_info", return_value={"test": "info"}):
        response = client.get("/api/system/info")
        assert response.status_code == 200
        assert response.json() == {"test": "info"}
