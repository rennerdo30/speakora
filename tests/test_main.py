import pytest
from click.testing import CliRunner
from tool.main import cli
from unittest.mock import patch, MagicMock
from pathlib import Path

@pytest.fixture
def runner():
    return CliRunner()

def test_info_command(runner):
    result = runner.invoke(cli, ["info"])
    assert result.exit_code == 0
    assert "platform" in result.output

def test_translate_command(runner, tmp_path):
    input_file = tmp_path / "test.wav"
    input_file.write_text("dummy")
    with patch("tool.main.SeamlessTranslator") as mock_translator:
        instance = mock_translator.return_value
        instance.translate_audio.return_value = {"status": "success", "target_file": "out.wav"}
        result = runner.invoke(cli, ["translate", "--input", str(input_file), "--target-lang", "deu"])
        assert result.exit_code == 0
        instance.translate_audio.assert_called_with(Path(input_file), "deu", "auto")

def test_translate_command_error(runner, tmp_path):
    input_file = tmp_path / "test.wav"
    input_file.write_text("dummy")
    with patch("tool.main.SeamlessTranslator") as mock_translator:
        instance = mock_translator.return_value
        instance.translate_audio.side_effect = Exception("Fail")
        result = runner.invoke(cli, ["translate", "--input", str(input_file), "--target-lang", "deu"])
        assert result.exit_code == 1

def test_download_command(runner):
    with patch("tool.main.SeamlessTranslator") as mock_translator:
        instance = mock_translator.return_value
        result = runner.invoke(cli, ["download", "--model-size", "small"])
        assert result.exit_code == 0
        assert instance.load_model.called

def test_gui_command(runner):
    with patch("uvicorn.run") as mock_run:
        with patch("tool.api.create_app") as mock_create:
            result = runner.invoke(cli, ["gui", "--port", "5001"])
            assert result.exit_code == 0
            assert mock_run.called

def test_worker_command(runner):
    with patch("tool.worker.Worker") as mock_worker:
        instance = mock_worker.return_value
        instance.start.side_effect = None
        result = runner.invoke(cli, ["worker"])
        assert result.exit_code == 0
        assert instance.start.called

def test_worker_command_keyboard_interrupt(runner):
    with patch("tool.worker.Worker") as mock_worker:
        instance = mock_worker.return_value
        instance.start.side_effect = KeyboardInterrupt()
        result = runner.invoke(cli, ["worker"])
        assert result.exit_code == 0
        assert "Stopping worker..." in result.output
        assert instance.stop.called

def test_job_submit_command(runner, tmp_path):
    input_file = tmp_path / "test.wav"
    input_file.write_text("dummy")
    with patch("tool.main.JobQueue") as mock_queue:
        instance = mock_queue.return_value
        instance.enqueue.return_value = "job_123"
        result = runner.invoke(cli, ["job", "submit", "--input", str(input_file), "--target-lang", "deu"])
        assert result.exit_code == 0
        assert "Submitted job: job_123" in result.output
        
        input_dir = tmp_path / "test_dir"
        input_dir.mkdir()
        (input_dir / "f1.wav").write_text("dummy")
        result = runner.invoke(cli, ["job", "submit", "--input", str(input_dir), "--target-lang", "deu"])
        assert result.exit_code == 0
        assert "Submitted 1 jobs" in result.output
        
        result = runner.invoke(cli, ["job", "submit", "--input", "invalid", "--target-lang", "deu"])
        assert "Invalid input path" in result.output

def test_job_list_command(runner):
    with patch("tool.main.JobQueue") as mock_queue:
        instance = mock_queue.return_value
        mock_job = MagicMock()
        mock_job.id = "job_123"
        mock_job.status = "queued"
        mock_job.input_file = "test.wav"
        instance.list_jobs.return_value = [mock_job]
        result = runner.invoke(cli, ["job", "list", "--status", "queued"])
        assert result.exit_code == 0
        assert "job_123" in result.output
        instance.list_jobs.assert_called_with("queued")
