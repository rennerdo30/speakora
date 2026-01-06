import logging
from tool.logger import setup_logger
from pathlib import Path

def test_setup_logger(tmp_path):
    log_file = tmp_path / "test.log"
    logger = setup_logger("test_logger", log_file=log_file)
    assert logger.name == "test_logger"
    assert len(logger.handlers) >= 1
    
    logger.info("test message")
    assert log_file.exists()
    content = log_file.read_text()
    assert "test message" in content

def test_setup_logger_no_file():
    logger = setup_logger("test_logger_no_file", console_enabled=True)
    assert logger.name == "test_logger_no_file"
    assert not any(isinstance(h, logging.FileHandler) for h in logger.handlers)
