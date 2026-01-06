import pytest
from pathlib import Path
from tool.config import load_config, Config

def test_load_config_defaults():
    cfg = load_config()
    assert cfg.model.size == "large"
    assert cfg.translation.target_lang == "eng"

def test_config_paths(test_config):
    assert "output" in str(test_config.paths.translated_path)
    assert "translated" in str(test_config.paths.translated_path)
    assert "metadata" in str(test_config.paths.metadata_path)
    assert "logs" in str(test_config.paths.logs_path)

def test_load_config_with_file(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("model:\n  size: 'small'\ntranslation:\n  target_lang: 'deu'")
    cfg = load_config(config_file)
    assert cfg.model.size == "small"
    assert cfg.translation.target_lang == "deu"

def test_load_config_env_overrides(monkeypatch):
    monkeypatch.setenv("SEAMLESS_DEVICE", "cuda")
    monkeypatch.setenv("SEAMLESS_MODEL_SIZE", "small")
    monkeypatch.setenv("INPUT_DIR", "/tmp/input")
    monkeypatch.setenv("OUTPUT_DIR", "/tmp/output")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    cfg = load_config()
    assert cfg.model.device == "cuda"
    assert cfg.model.size == "small"
    assert cfg.paths.input_dir == "/tmp/input"
    assert cfg.paths.output_dir == "/tmp/output"
    assert cfg.logging.level == "DEBUG"
