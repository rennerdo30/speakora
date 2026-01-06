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

def test_create_job(client, tmp_path):
    # Create input file so validation passes
    input_file = tmp_path / "test.wav"
    input_file.write_text("dummy")
    
    with patch("tool.api.JobQueue.enqueue", return_value="job_123"):
        response = client.post("/api/jobs", json={
            "input_file": str(input_file),
            "target_lang": "deu",
            "source_lang": "auto",
            "priority": 0
        })
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

def test_get_job_logs(client, tmp_path):
    # Retrieve the config object used by the app
    # FastAPITestClient.app is the FastAPI app. state might store it if we put it there?
    # Actually, create_app closes over 'cfg'.
    # But 'client' fixture is created with 'test_config' fixture.
    # The 'test_config' fixture is likely module/session scoped or function scoped?
    # Let's see conftest.py or test_api.py. 
    # test_api.py uses 'test_config' fixture.
    
    # We can't easily modify the captured closure variable 'cfg' inside create_app.
    # But since Python objects are mutable, if we modify the object passed to create_app...
    # But create_app was already called in the 'client' fixture.
    # So we need to modify the SAME object instance.
    pass

# We should redefine the tests to explicitely create the app with modified config
# or rely on the fact that test_config is mutable.

def test_get_job_logs(test_config, tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "app.log"
    log_file.write_text("line1\nline2")
    
    test_config.paths.output_dir = str(tmp_path)
    test_config.paths.logs_subdir = "logs"
    
    app = create_app(test_config)
    client = TestClient(app)
    
    response = client.get("/api/jobs/job_123/logs")
    assert response.status_code == 200
    assert "line2" in response.json()["logs"]

def test_get_job_logs_not_found(test_config, tmp_path):
    test_config.paths.output_dir = str(tmp_path)
    test_config.paths.logs_subdir = "logs"
    
    app = create_app(test_config)
    client = TestClient(app)
    
    response = client.get("/api/jobs/job_123/logs")
    assert response.status_code == 200
    assert "No logs found" in response.json()["logs"]

def test_cancel_job(client):
    with patch("tool.api.JobQueue.update_job_status") as mock_update:
        response = client.delete("/api/jobs/job_123")
        assert response.status_code == 200
        assert mock_update.called

def test_download_model(client):
    with patch("tool.api.SeamlessTranslator") as mock_translator:
        mock_instance = mock_translator.return_value
        response = client.post("/api/system/download", json={"model_size": "small"})
        assert response.status_code == 200
        # Check if background task ran (TestClient runs them)
        assert mock_instance.load_model.called

def test_config_endpoints(client):
    response = client.get("/api/system/config")
    assert response.status_code == 200
    
    response = client.patch("/api/system/config", json={"model": {"size": "medium"}})
    assert response.status_code == 200
    assert response.json()["model"]["size"] == "medium"

