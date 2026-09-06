from tool.worker import Worker
from tool.job_queue import JobQueue, JobStatus
from tool.config import Config
from unittest.mock import patch
import pytest


@pytest.fixture
def mock_worker(tmp_path, monkeypatch):
    monkeypatch.setattr("tool.worker.signal.signal", lambda *args: None)
    # Setup Config and DB
    cfg = Config()
    cfg.paths.output_dir = str(tmp_path)
    (tmp_path / "translated").mkdir()

    # Create DB and Queue
    db_path = tmp_path / "jobs.db"
    queue = JobQueue(db_path)

    # Mock Translator
    with patch("tool.worker.SeamlessTranslator") as mock_translator:
        worker = Worker(cfg, worker_id="worker-main")
        worker.queue = queue  # Use real queue
        return worker, queue, mock_translator


def test_worker_resets_stale_jobs(mock_worker):
    worker, queue, _ = mock_worker

    # Manually add a RUNNING job
    job_id = queue.enqueue("input.wav", "deu")
    queue.update_job_status(job_id, JobStatus.RUNNING)

    # Verify it is RUNNING
    job = queue.get_job(job_id)
    assert job.status == JobStatus.RUNNING

    # Start worker (only checking the start logic, not the loop)
    # We patch the run loop to exit immediately or just verify the startup logic
    # The simplest is to set running=False immediately after load_model
    # But start() has a while loop.
    # We should extract reset logic or patch the threading/loop?
    # Or just subclass/inject?

    # Let's just manually run the logic we inserted, or trust the integration?
    # Better: Run start in a thread for a split second? No, too complex.
    # We'll just execute the lines added.
    # But for a proper test, let's mock load_model to stop the worker loop by raising an exception we catch?

    worker.translator.load_model.side_effect = KeyboardInterrupt("Stop")

    try:
        worker.start()
    except KeyboardInterrupt:
        pass

    # Verify status is FAILED
    job = queue.get_job(job_id)
    assert job.status == JobStatus.FAILED
    assert "Worker restarted" in job.error_message


def test_secondary_worker_preserves_running_jobs(mock_worker):
    worker, queue, _ = mock_worker
    worker.worker_id = "worker-secondary"
    job_id = queue.enqueue("input.wav", "deu")
    queue.update_job_status(job_id, JobStatus.RUNNING)
    worker.translator.load_model.side_effect = KeyboardInterrupt("Stop")
    with pytest.raises(KeyboardInterrupt):
        worker.start()
    assert queue.get_job(job_id).status == JobStatus.RUNNING


def test_progress_callback_does_not_fail_the_job(mock_worker):
    worker, queue, _ = mock_worker
    job_id = queue.enqueue("input.wav", "deu")

    def translate(*args, progress_callback, **kwargs):
        progress_callback(0.5)
        worker.running = False

    worker.translator.translate_audio.side_effect = translate
    worker.start()
    assert queue.get_job(job_id).status == JobStatus.COMPLETED
