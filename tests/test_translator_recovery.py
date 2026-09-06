from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest
import torch
from tool.translator import SeamlessTranslator


@pytest.fixture
def translator(test_config):
    test_config.model.device = "cpu"
    model = MagicMock()
    processor = MagicMock()
    encoding = MagicMock()
    encoding.to.return_value = encoding
    encoding.items.return_value = [
        ("input_features", torch.ones(1, 8)),
        ("padding", None),
    ]
    processor.return_value = encoding
    processor.batch_decode.return_value = ["translated", "translated"]
    model.generate.return_value = SimpleNamespace(
        waveform=torch.ones(2, 1, 16), sequences=torch.ones(2, 3)
    )
    manager = MagicMock()
    manager.load_model.return_value = (model, processor)
    result = SeamlessTranslator(test_config, manager)
    result.audio_processor = MagicMock()
    result.audio_processor.load_audio.return_value = (torch.ones(1, 50), 4)
    return result


def test_detection_truncates_sample_and_falls_back_when_duration_missing(
    translator, monkeypatch
):
    monkeypatch.setattr(
        "librosa.get_duration",
        lambda **_: (_ for _ in ()).throw(ValueError("no duration")),
    )
    assert translator.detect_language(Path("input.wav")) == "eng"
    assert len(translator.processor.call_args.kwargs["audios"]) == 40
    assert translator.model.generate.call_args.kwargs["src_lang"] is None


def test_reference_audio_recovers_after_read_failure(translator):
    translator._load_reference_audio(Path("reference.wav"))
    assert translator._reference_audio_path == Path("reference.wav")
    translator.expressive_mode = True
    parameters = translator._apply_expressive_mode({"temperature": 0.5, "num_beams": 1})
    assert parameters == {"temperature": 0.7, "num_beams": 5}
    translator.audio_processor.load_audio.side_effect = OSError("unreadable")
    translator._load_reference_audio(Path("bad.wav"))
    assert translator._reference_audio_features is None
    assert translator._reference_audio_path is None


@pytest.mark.parametrize("reference", [False, True])
def test_partial_batch_and_expressive_translation(
    translator, tmp_path, monkeypatch, reference
):
    source = tmp_path / "input.wav"
    source.write_bytes(b"audio")
    translator.config.processing.batch_size = 2
    translator.expressive_mode = True
    translator.audio_processor.stream_audio.return_value = [(torch.ones(1, 8), 4)] * 3
    monkeypatch.setattr(
        "soundfile.info", lambda _: SimpleNamespace(frames=480, samplerate=4)
    )
    monkeypatch.setattr(
        translator,
        "detect_language",
        (
            MagicMock(return_value="fra")
            if reference
            else MagicMock(side_effect=RuntimeError("detection failed"))
        ),
    )
    progress = MagicMock()
    result = translator.translate_audio(
        source,
        "deu",
        reference_audio=source if reference else None,
        progress_callback=progress,
    )
    assert result["status"] == "success"
    assert translator.model.generate.call_count == 2
    assert translator.model.generate.call_args.kwargs["src_lang"] == (
        "fra" if reference else "eng"
    )
    assert translator._reference_audio_path == source
    assert progress.call_count >= 2
    translator.audio_processor.save_audio.assert_called_once()


def test_empty_audio_is_reported(translator):
    translator.audio_processor.stream_audio.return_value = []
    result = translator.translate_audio(Path("empty.wav"), "deu", source_lang="eng")
    assert result["status"] == "failed"
    translator.audio_processor.save_audio.assert_not_called()


def test_long_stream_bounds_context_and_handles_object_output(translator):
    chunk = (np.ones(20000) * 16000).astype(np.int16).tobytes()
    translator.load_model()
    translator.model.generate.return_value = SimpleNamespace(
        waveform=torch.ones(1, 1, 40000), sequences=torch.ones(1, 3)
    )
    for _ in range(7):
        audio, text = translator.translate_audio_stream(chunk, "deu")
        assert text == "translated"
        assert audio
    assert len(translator._streaming_context["audio_buffer"]) == 5
    assert len(translator._streaming_context["text_history"]) == 5
    assert len(translator.processor.call_args.kwargs["audios"]) == 32000


def test_accelerator_inputs_use_configured_precision(translator, monkeypatch):
    original_to = torch.Tensor.to

    def simulated_device(tensor, destination, *args, **kwargs):
        if destination == "test-accelerator":
            return tensor
        return original_to(tensor, destination, *args, **kwargs)

    monkeypatch.setattr(torch.Tensor, "to", simulated_device)
    translator.device = "test-accelerator"
    translator.config.model.dtype = "float16"
    monkeypatch.setattr("librosa.get_duration", lambda **_: 1)
    translator.detect_language(Path("input.wav"))
    assert (
        translator.model.generate.call_args.kwargs["input_features"].dtype
        == torch.float16
    )
    translator._load_reference_audio(Path("reference.wav"))
    assert translator._reference_audio_path is not None
    translator.audio_processor.stream_audio.return_value = [(torch.ones(1, 8), 4)]
    result = translator.translate_audio(Path("input.wav"), "deu", source_lang="eng")
    assert result["status"] == "success"
    assert (
        translator.model.generate.call_args.kwargs["input_features"].dtype
        == torch.float16
    )
    translator.model.generate.return_value = SimpleNamespace(
        waveform=torch.ones(1, 1, 16), sequences=torch.ones(1, 3)
    )
    translator.translate_audio_stream(
        (np.ones(10) * 16000).astype(np.int16).tobytes(), "deu"
    )
    assert (
        translator.model.generate.call_args.kwargs["input_features"].dtype
        == torch.float16
    )


def test_no_generated_audio_is_not_success(translator, monkeypatch):
    translator.audio_processor.stream_audio.return_value = [(torch.ones(1, 8), 4)]
    monkeypatch.setattr(translator, "_process_batch_and_append", lambda *_: None)
    result = translator.translate_audio(Path("input.wav"), "deu", source_lang="eng")
    assert result["status"] == "failed"
    assert result["error"] == "No translated audio was generated"
    translator.audio_processor.save_audio.assert_not_called()
