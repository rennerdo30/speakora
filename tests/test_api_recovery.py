import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from tool import api
from tool.job_queue import JobStatus


@pytest.fixture
def api_client(test_config, job_queue, monkeypatch):
    monkeypatch.setattr(api, "JobQueue", lambda _: job_queue)
    return TestClient(api.create_app(test_config))


def test_stats_and_checkpoint_history(api_client, job_queue, tmp_path):
    assert api_client.get("/api/stats").json()["total_jobs"] == 0
    job = job_queue.enqueue("audio.wav", "deu")
    other = job_queue.enqueue("other.wav", "fra")
    assert api_client.get("/api/stats").json()["completion_rate"] == 0
    job_queue.save_checkpoint(job, {"progress": 0.5}, 120)
    checkpoints = api_client.get(f"/api/jobs/{job}/checkpoints").json()["checkpoints"]
    assert checkpoints[0]["audio_position"] == 120
    assert api_client.get("/api/jobs/missing/checkpoints").status_code == 404
    job_queue.update_job_status(job, JobStatus.COMPLETED, processing_time_seconds=12)
    job_queue.update_job_status(other, JobStatus.FAILED)
    stats = api_client.get("/api/stats").json()
    assert stats["completion_rate"] == 50
    assert stats["average_processing_time"] == 12
    assert stats["total_processing_time"] == 12
    assert stats["by_language"] == {"deu": 1, "fra": 1}
    audio = tmp_path / "input.wav"
    audio.write_bytes(b"audio")
    response = api_client.post(
        "/api/jobs",
        json={
            "input_file": str(audio),
            "target_lang": "deu",
            "reference_audio": str(audio),
        },
    )
    assert response.status_code == 200
    response = api_client.post(
        "/api/jobs",
        json={
            "input_file": str(audio),
            "target_lang": "deu",
            "reference_audio": str(audio) + "missing",
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize("hardware", ["cpu", "cuda", "mps", "mps-error", "no-psutil"])
def test_status_reports_available_hardware(api_client, monkeypatch, hardware):
    psutil = MagicMock()
    psutil.cpu_percent.return_value = 25
    psutil.cpu_count.return_value = 4
    psutil.virtual_memory.return_value = SimpleNamespace(
        total=4096, available=2048, used=2048, percent=50
    )
    monkeypatch.setitem(
        sys.modules, "psutil", None if hardware == "no-psutil" else psutil
    )
    with patch("torch.cuda.is_available", return_value=hardware == "cuda"), patch(
        "torch.cuda.memory_allocated", return_value=1024
    ), patch("torch.cuda.memory_reserved", return_value=2048), patch(
        "torch.cuda.get_device_properties",
        return_value=SimpleNamespace(total_memory=4096),
    ), patch(
        "torch.backends.mps.is_available", return_value=hardware.startswith("mps")
    ), patch(
        "tool.device_manager.get_device_info", return_value={"device": hardware}
    ), patch(
        "subprocess.run",
        side_effect=RuntimeError("unavailable") if hardware == "mps-error" else None,
    ):
        response = api_client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["queue"]["total"] == 0
    assert data["cpu"]["count"] == (1 if hardware == "no-psutil" else 4)
    if hardware == "cuda":
        assert data["gpu_memory"]["total_mb"] == 4096 / 1024**2
    if hardware.startswith("mps"):
        assert data["gpu_memory"]["available"] is True


@pytest.mark.parametrize("built", [False, True])
def test_frontend_routes_do_not_swallow_api_routes(
    test_config, monkeypatch, tmp_path, built
):
    source = tmp_path / "tool" / "api.py"
    monkeypatch.setattr(api, "__file__", str(source))
    dist = tmp_path / "frontend" / "dist"
    if built:
        (dist / "assets").mkdir(parents=True)
        (dist / "index.html").write_text("frontend ready")
    client = TestClient(api.create_app(test_config))
    assert client.get("/").status_code == 200
    if built:
        assert client.get("/settings").text == "frontend ready"
        assert client.get("/api/missing").status_code == 404
        assert client.get("/favicon.ico").status_code == 404
        (dist / "favicon.ico").write_bytes(b"icon")
        assert client.get("/favicon.ico").content == b"icon"


def test_stream_translation_recovers_after_failed_chunk(api_client):
    translator = MagicMock()
    translator.translate_audio_stream.side_effect = [
        RuntimeError("bad audio"),
        (b"audio", "Hallo"),
    ]
    with patch.object(api, "SeamlessTranslator", return_value=translator):
        with api_client.websocket_connect("/api/ws/translate") as ws:
            ws.send_json({"type": "init", "target_lang": "deu"})
            ws.send_bytes(b"bad")
            assert ws.receive_json()["error"] == "bad audio"
            ws.send_bytes(b"valid")
            assert ws.receive_json() == {"status": "success", "text": "Hallo"}


def test_job_progress_reports_completion_and_missing_jobs(api_client, job_queue):
    with api_client.websocket_connect("/ws/jobs/missing") as ws:
        assert ws.receive_json()["error"] == "Job not found"
    job = job_queue.enqueue("audio.wav", "deu")
    job_queue.update_job_status(job, JobStatus.COMPLETED, progress_percent=100)
    with api_client.websocket_connect(f"/ws/jobs/{job}") as ws:
        assert ws.receive_json()["progress_percent"] == 100
        assert ws.receive_json()["final"] is True


def test_job_progress_handles_polling_failure(api_client, job_queue):
    job = job_queue.enqueue("audio.wav", "deu")

    async def unavailable(_):
        raise RuntimeError("polling interrupted")

    with patch.object(api.asyncio, "sleep", unavailable):
        with api_client.websocket_connect(f"/ws/jobs/{job}") as ws:
            assert ws.receive_json()["status"] == "queued"


@pytest.mark.parametrize(
    "payload", [{"audio": None}, {"audio": {"target_sample_rate": "invalid"}}]
)
def test_invalid_config_is_rejected_atomically(api_client, payload):
    before = api_client.get("/api/system/config").json()
    assert api_client.patch("/api/system/config", json=payload).status_code == 422
    assert api_client.get("/api/system/config").json() == before
