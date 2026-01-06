import pytest
import torch
import numpy as np
from pathlib import Path
from tool.audio_processor import AudioProcessor
import soundfile as sf

@pytest.fixture
def sample_audio_file(tmp_path):
    file_path = tmp_path / "test_audio.wav"
    # Create a 1-second 1kHz sine wave
    sr = 44100
    t = np.linspace(0, 1, sr)
    audio = 0.5 * np.sin(2 * np.pi * 1000 * t)
    sf.write(str(file_path), audio, sr)
    return file_path

def test_load_audio(sample_audio_file):
    processor = AudioProcessor(target_sample_rate=16000)
    waveform, sr = processor.load_audio(sample_audio_file)
    
    assert sr == 16000
    assert waveform.dim() == 2
    assert waveform.shape[0] == 1 # Mono
    assert torch.abs(waveform).max() <= 1.0

def test_save_audio(tmp_path):
    processor = AudioProcessor(target_sample_rate=16000)
    waveform = torch.randn(1, 16000)
    output_path = tmp_path / "output.wav"
    
    processor.save_audio(waveform, output_path)
    assert output_path.exists()
    
    # Reload and check
    reloaded_waveform, sr = processor.load_audio(output_path)
    assert sr == 16000
    assert reloaded_waveform.shape == (1, 16000)

def test_save_audio_1d(tmp_path):
    processor = AudioProcessor()
    waveform = torch.randn(16000)
    output_path = tmp_path / "output_1d.wav"
    processor.save_audio(waveform, output_path)
    assert output_path.exists()

def test_load_audio_error():
    processor = AudioProcessor()
    with pytest.raises(Exception):
        processor.load_audio("non_existent.wav")

    with pytest.raises(Exception):
        processor.save_audio(torch.randn(1, 100), "")

def test_stream_audio(sample_audio_file):
    processor = AudioProcessor(target_sample_rate=16000)
    
    # 1 second audio at 44.1kHz.
    # We request 0.5s chunks.
    # Should get roughly 2 chunks appropriately resampled to 16kHz.
    
    chunks = list(processor.stream_audio(sample_audio_file, chunk_duration_sec=0.5))
    
    assert len(chunks) == 2
    
    for wav, sr in chunks:
        assert sr == 16000
        assert wav.dim() == 2
        assert wav.shape[0] == 1 # Mono
        # 0.5 sec * 16000 = 8000 samples
        assert 7900 < wav.shape[1] < 8100 # Approx match due to resampling/rounding
