import pytest
from tool.job_queue import JobQueue, JobStatus

def test_enqueue_and_list(job_queue):
    job_id = job_queue.enqueue("input.wav", "deu", priority=10)
    assert job_id is not None
    
    jobs = job_queue.list_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == job_id
    assert jobs[0].priority == 10
    
    # Test filtering
    jobs = job_queue.list_jobs(status=JobStatus.QUEUED)
    assert len(jobs) == 1
    jobs = job_queue.list_jobs(status=JobStatus.COMPLETED)
    assert len(jobs) == 0

def test_update_status(job_queue):
    job_id = job_queue.enqueue("input.wav", "deu")
    
    # Run
    job_queue.update_job_status(job_id, JobStatus.RUNNING)
    job = job_queue.get_job(job_id)
    assert job.status == JobStatus.RUNNING
    assert job.started_at is not None
    
    # Pause
    job_queue.update_job_status(job_id, JobStatus.PAUSED)
    job = job_queue.get_job(job_id)
    assert job.status == JobStatus.PAUSED
    assert job.paused_at is not None
    
    # Resume
    job_queue.update_job_status(job_id, JobStatus.RUNNING)
    job = job_queue.get_job(job_id)
    assert job.resumed_at is not None
    
    # Complete
    job_queue.update_job_status(job_id, JobStatus.COMPLETED, progress_percent=100.0)
    job = job_queue.get_job(job_id)
    assert job.status == JobStatus.COMPLETED
    assert job.completed_at is not None
    assert job.progress_percent == 100.0

def test_checkpoint(job_queue):
    job_id = job_queue.enqueue("input.wav", "deu")
    job_queue.save_checkpoint(job_id, {"data": "test"}, audio_position=100)
    
    checkpoint = job_queue.get_latest_checkpoint(job_id)
    assert checkpoint.audio_position == 100
    assert checkpoint.checkpoint_data == {"data": "test"}

def test_get_non_existent_job(job_queue):
    assert job_queue.get_job("non-existent") is None
