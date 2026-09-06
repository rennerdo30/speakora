from unittest.mock import MagicMock

import pytest
from tool.worker import Worker
from tool.job_queue import JobStatus


@pytest.fixture
def worker(test_config, job_queue, monkeypatch):
    monkeypatch.setattr("tool.worker.signal.signal", lambda *_: None)
    monkeypatch.setattr("tool.worker.SeamlessTranslator", lambda _: MagicMock())
    instance = Worker(test_config, worker_id="secondary")
    instance.queue = job_queue
    return instance


@pytest.mark.parametrize(
    "error", [RuntimeError("translation failed"), KeyboardInterrupt()]
)
def test_translation_failure_or_interrupt_updates_job(worker, error):
    job = worker.queue.enqueue("input.wav", "deu")

    def translate(*_, **kwargs):
        worker.running = False
        raise error

    worker.translator.translate_audio.side_effect = translate
    worker.start()
    expected = (
        JobStatus.PAUSED if isinstance(error, KeyboardInterrupt) else JobStatus.FAILED
    )
    assert worker.queue.get_job(job).status == expected


@pytest.mark.parametrize("queue_error", [False, True])
def test_idle_and_failed_poll_can_stop(worker, monkeypatch, queue_error):
    if queue_error:
        monkeypatch.setattr(
            worker.queue,
            "list_jobs",
            MagicMock(side_effect=RuntimeError("database busy")),
        )
    monkeypatch.setattr("tool.worker.time.sleep", lambda _: worker.stop())
    worker.start()
    assert not worker.running
    worker.translator.translate_audio.assert_not_called()


@pytest.mark.parametrize("checkpoint_error", [False, True])
@pytest.mark.parametrize("reference", [None, "speaker.wav"])
def test_expressive_job_and_checkpoint_recovery(
    worker, monkeypatch, checkpoint_error, reference
):
    job = worker.queue.enqueue(
        "input.wav", "deu", expressive=True, reference_audio=reference
    )
    worker.queue.save_checkpoint(job, {"progress": 0.1}, 10)
    clock = [0]
    monkeypatch.setattr("tool.worker.time.time", lambda: clock[0])
    if checkpoint_error:
        monkeypatch.setattr(
            worker.queue,
            "save_checkpoint",
            MagicMock(side_effect=RuntimeError("disk full")),
        )

    def translate(*_, progress_callback, reference_audio, **kwargs):
        assert str(reference_audio) == (reference or "input.wav")
        clock[0] = 400
        progress_callback(0.5)
        worker.running = False

    worker.translator.translate_audio.side_effect = translate
    worker.start()
    assert worker.queue.get_job(job).status == JobStatus.COMPLETED
    if not checkpoint_error:
        assert (
            worker.queue.get_latest_checkpoint(job).checkpoint_data["progress"] == 0.5
        )


@pytest.mark.parametrize("signal", [False, True])
def test_shutdown_pauses_current_job(worker, signal):
    job = worker.queue.enqueue("input.wav", "deu")
    worker.current_job_id = job
    worker.running = True
    if signal:
        worker._signal_handler(15, None)
    else:
        worker.stop()
    assert not worker.running
    assert worker.queue.get_job(job).status == JobStatus.PAUSED


def test_failed_translation_result_marks_job_failed(worker, monkeypatch):
    job = worker.queue.enqueue("empty.wav", "deu")
    worker.translator.translate_audio.return_value = {
        "status": "failed",
        "error": "Empty audio",
    }
    monkeypatch.setattr("tool.worker.time.sleep", lambda _: worker.stop())
    worker.start()
    result = worker.queue.get_job(job)
    assert result.status == JobStatus.FAILED
    assert result.error_message == "Empty audio"
