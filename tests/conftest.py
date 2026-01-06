import pytest
import os
from pathlib import Path
from tool.config import Config, load_config
from tool.job_queue import JobQueue

@pytest.fixture
def test_config(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "translated").mkdir()
    (output_dir / "logs").mkdir()
    (output_dir / "metadata").mkdir()
    
    cfg = Config()
    cfg.paths.output_dir = str(output_dir)
    cfg.paths.input_dir = str(tmp_path / "input")
    return cfg

@pytest.fixture
def job_queue(tmp_path):
    db_path = tmp_path / "test_jobs.db"
    return JobQueue(db_path)
