import pytest
from unittest.mock import patch, MagicMock
from tool.worker import Worker
from tool.job_queue import JobStatus
from pathlib import Path
import time

def test_worker_loop(test_config):
    with patch("tool.worker.JobQueue") as mock_queue:
        with patch("tool.worker.SeamlessTranslator") as mock_translator:
            worker = Worker(test_config)
            
            mock_job = MagicMock()
            mock_job.id = "job_123"
            mock_job.status = JobStatus.QUEUED
            mock_job.input_file = "test.wav"
            mock_job.target_lang = "deu"
            
            queue_instance = mock_queue.return_value
            queue_instance.list_jobs.side_effect = [[mock_job], []]
            
            # Use a mock for time.sleep to avoid hanging and also to break the loop
            with patch("time.sleep", side_effect=[None, KeyboardInterrupt]):
                try:
                    worker.start()
                except KeyboardInterrupt:
                    pass
            
            assert queue_instance.update_job_status.called
            assert mock_translator.return_value.translate_audio.called

def test_worker_processing_error(test_config):
    with patch("tool.worker.JobQueue") as mock_queue:
        with patch("tool.worker.SeamlessTranslator") as mock_translator:
            worker = Worker(test_config)
            
            mock_job = MagicMock()
            mock_job.id = "job_123"
            mock_job.input_file = "test.wav"
            
            queue_instance = mock_queue.return_value
            queue_instance.list_jobs.side_effect = [[mock_job]]
            
            mock_translator.return_value.translate_audio.side_effect = Exception("Translate fail")
            
            with patch("time.sleep", side_effect=KeyboardInterrupt):
                try:
                    worker.start()
                except KeyboardInterrupt:
                    pass
            
            # Check if status was updated to FAILED
            calls = queue_instance.update_job_status.call_args_list
            assert any(c[0][1] == JobStatus.FAILED for c in calls)

def test_worker_stop(test_config):
    worker = Worker(test_config)
    worker.running = True
    worker.stop()
    assert worker.running is False
