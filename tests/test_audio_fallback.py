import runpy
from unittest.mock import patch

import numpy as np
import pytest
import torch
from tool import audio_processor


@pytest.mark.parametrize("stereo", [False, True])
def test_decoder_fallback_preserves_samples_and_normalizes(monkeypatch, stereo):
    signal = np.array([0.25, -0.5, 0.25, -0.5], dtype=np.float32)
    if stereo:
        signal = np.stack([signal, signal])
    monkeypatch.setattr(audio_processor, "_FFMPEG_AVAILABLE", False)
    monkeypatch.setattr("librosa.get_duration", lambda **_: 1)
    monkeypatch.setattr("librosa.load", lambda *_, **kwargs: (signal, 4))
    monkeypatch.setattr(
        "torchaudio.load",
        lambda *_: (_ for _ in ()).throw(RuntimeError("unsupported codec")),
    )
    processor = audio_processor.AudioProcessor(target_sample_rate=4)
    chunks = list(processor.stream_audio("input.mp3", 0.5))
    assert len(chunks) == 2
    assert all(rate == 4 and data.shape == (1, 2) for data, rate in chunks)
    assert torch.equal(chunks[0][0], torch.tensor([[0.5, -1.0]]))
    loaded, rate = processor.load_audio("input.mp3")
    assert rate == 4
    assert loaded.abs().max() == 1


def test_streaming_reports_decode_failure(monkeypatch):
    monkeypatch.setattr(
        "librosa.get_duration",
        lambda **_: (_ for _ in ()).throw(ValueError("invalid audio")),
    )
    with pytest.raises(ValueError, match="invalid audio"):
        list(audio_processor.AudioProcessor().stream_audio("broken.wav"))


def test_missing_ffmpeg_is_reported(caplog):
    with patch("subprocess.run", side_effect=FileNotFoundError("ffmpeg")):
        probe = runpy.run_path(audio_processor.__file__)
        assert probe["_check_ffmpeg"]() is False
        assert "ffmpeg not found" in caplog.text


def test_native_decoder_resamples_and_downmixes(monkeypatch):
    from unittest.mock import MagicMock

    monkeypatch.setattr("librosa.get_duration", lambda **_: 1)
    monkeypatch.setattr("librosa.load", lambda *_, **kwargs: (np.ones(8), 8))
    waveform = torch.tensor([[0.25, 0.5, -0.5, 0.5, 0.25, 0.5, -0.5, 0.5]] * 2)
    monkeypatch.setattr("torchaudio.load", lambda _: (waveform, 8))
    resample = MagicMock(return_value=lambda wave: wave[:, ::2])
    monkeypatch.setattr("torchaudio.transforms.Resample", resample)
    chunks = list(
        audio_processor.AudioProcessor(target_sample_rate=4).stream_audio(
            "stereo.wav", 0.5
        )
    )
    resample.assert_called_once_with(8, 4)
    assert len(chunks) == 2
    assert all(
        rate == 4 and torch.equal(data, torch.tensor([[0.5, -1.0]]))
        for data, rate in chunks
    )
