import pytest
from fastapi.testclient import TestClient
from tool.api import create_app
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
        response = client.post(
            "/api/jobs",
            json={
                "input_file": str(input_file),
                "target_lang": "deu",
                "source_lang": "auto",
                "priority": 0,
            },
        )
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


def test_auth_middleware(test_config, tmp_path):
    test_config.security.api_key = "secret_key"
    app = create_app(test_config)
    client = TestClient(app)

    # Without header
    response = client.get("/api/jobs")
    assert response.status_code == 401

    # With wrong header
    response = client.get("/api/jobs", headers={"X-API-KEY": "wrong"})
    assert response.status_code == 401

    # With correct header
    with patch("tool.api.JobQueue.list_jobs", return_value=[]):
        response = client.get("/api/jobs", headers={"X-API-KEY": "secret_key"})
        assert response.status_code == 200

    # WebSocket Logic
    from starlette.websockets import WebSocketDisconnect

    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/api/ws/translate?key=wrong"):
            pass
    assert excinfo.value.code == 1008

    # Recreate app to clear settings or use clean fixture
    test_config.security.api_key = None


def test_rate_limiting(test_config):
    """Test that rate limiting works correctly."""
    app = create_app(test_config)
    client = TestClient(app)

    # Make many requests quickly
    responses = []
    for i in range(105):  # Exceed the limit of 100
        with patch("tool.api.JobQueue.list_jobs", return_value=[]):
            response = client.get("/api/jobs")
            responses.append(response.status_code)

    # Should have some 429 responses after limit exceeded
    # Note: Rate limiting is per IP, and TestClient might use same IP
    # So we expect some 429s in the later requests
    assert 429 in responses or len([r for r in responses if r == 200]) <= 100


def test_websocket_context_reset(test_config):
    """Test WebSocket context reset functionality."""
    test_config.security.api_key = None  # Disable auth for simpler test
    app = create_app(test_config)
    client = TestClient(app)

    with patch("tool.api.SeamlessTranslator") as mock_translator_class:
        mock_translator = MagicMock()
        mock_translator_class.return_value = mock_translator
        mock_translator.load_model.return_value = None

        with client.websocket_connect("/api/ws/translate") as websocket:
            # Send init message
            websocket.send_json(
                {"type": "init", "target_lang": "deu", "source_lang": "eng"}
            )

            # Send reset message
            websocket.send_json({"type": "reset"})

            # Should receive context_reset response
            response = websocket.receive_json()
            assert response["status"] == "context_reset"
            assert mock_translator.reset_streaming_context.called

    test_config.security.api_key = None
