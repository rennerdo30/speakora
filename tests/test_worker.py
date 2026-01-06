from tool.worker import Worker
from tool.job_queue import JobQueue, JobStatus, Job
from tool.config import Config
from unittest.mock import MagicMock, patch
import pytest

@pytest.fixture
def mock_worker(tmp_path):
    # Setup Config and DB
    cfg = Config()
    cfg.paths.output_dir = str(tmp_path)
    (tmp_path / "translated").mkdir()
    
    # Create DB and Queue
    db_path = tmp_path / "jobs.db"
    queue = JobQueue(db_path)
    
    # Mock Translator
    with patch("tool.worker.SeamlessTranslator") as mock_translator:
        worker = Worker(cfg)
        worker.queue = queue # Use real queue
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
