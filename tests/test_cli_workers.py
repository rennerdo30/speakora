from unittest.mock import MagicMock
import pytest
from click.testing import CliRunner
from tool.main import cli
from tool.config import load_config


@pytest.mark.parametrize("interrupt", [False, True])
def test_multiple_workers_start_and_stop(monkeypatch, interrupt):
    workers = []

    def make_worker(*args, **kwargs):
        worker = MagicMock()
        workers.append(worker)
        return worker

    monkeypatch.setattr("tool.worker.Worker", make_worker)

    class Thread:
        def __init__(self, target, args, daemon):
            self.target, self.args, self.interrupted = target, args, False

        def start(self):
            self.target(*self.args)

        def join(self, timeout=None):
            if interrupt and timeout is None and not self.interrupted:
                self.interrupted = True
                raise KeyboardInterrupt

    monkeypatch.setattr("threading.Thread", Thread)
    result = CliRunner().invoke(cli, ["worker", "--num-workers", "2"])
    assert result.exit_code == 0
    assert len(workers) == 2
    for worker in workers:
        worker.start.assert_called_once()
        assert worker.stop.called == interrupt


def test_log_level_environment(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    assert load_config().logging.level == "DEBUG"


def test_api_key_environment(monkeypatch):
    monkeypatch.setenv("SEAMLESS_API_KEY", "test-only-key")
    assert load_config().security.api_key == "test-only-key"
