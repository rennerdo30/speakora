import pytest
from click.testing import CliRunner
from tool.main import cli
from tool.languages import validate_language
from fastapi.testclient import TestClient
from tool.api import create_app
from tool.config import load_config

def test_language_validation_utility():
    assert validate_language("deu") is True
    assert validate_language("eng") is True
    assert validate_language("auto") is True
    assert validate_language("xyz") is False
    assert validate_language("") is False

def test_get_language_name():
    from tool.languages import get_language_name
    assert get_language_name("deu") == "German"
    assert get_language_name("xyz") == "Unknown"

def test_cli_translate_validation(tmp_path):
    input_file = tmp_path / "test.wav"
    input_file.write_text("dummy")
    runner = CliRunner()
    result = runner.invoke(cli, ["translate", "--input", str(input_file), "--target-lang", "xyz"])
    assert result.exit_code == 1
    assert "Unsupported language code" in result.output

def test_cli_job_submit_validation():
    runner = CliRunner()
    # Mocking config/output dir might be needed if not handled by fixtures
    # But validation happens before DB init in the modified code
    result = runner.invoke(cli, ["job", "submit", "--input", "test.wav", "--target-lang", "xyz"])
    assert result.exit_code == 0 # It returns early with error message, click default exit code 0 unless exception/sys.exit
    # wait, I used `return` in job_submit, so exit code 0.
    # In translate I used `sys.exit(1)`.
    assert "Unsupported language code" in result.output

def test_api_validation(tmp_path):
    # Mock config
    cfg = load_config()
    cfg.paths.output_dir = str(tmp_path)
    
    app = create_app(cfg)
    client = TestClient(app)
    
    # Valid job
    response = client.post("/api/jobs", json={
        "input_file": "/tmp/audio.wav",
        "target_lang": "fra"
    })
    # Since /tmp/audio.wav doesn't exist, it should return 400 (Input file does not exist)
    assert response.status_code == 400
    assert "Input file does not exist" in response.json()['detail']
    
    # Invalid lang
    response = client.post("/api/jobs", json={
        "input_file": "/tmp/audio.wav",
        "target_lang": "xyz"
    })
    assert response.status_code == 400
    assert "Unsupported target language" in response.json()['detail']
