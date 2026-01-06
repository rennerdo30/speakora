import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import torch
from tool.translator import SeamlessTranslator
from tool.config import Config

@pytest.fixture
def mock_translator(test_config):
    with patch("tool.translator.ModelManager") as mock_mm:
        # Mock load_model to return mock model and processor
        mock_model = MagicMock()
        mock_processor = MagicMock()
        
        # Mock generate output: (audio, text)
        mock_model.generate.return_value = (torch.zeros(1, 16000), torch.tensor([[1, 2, 3]]))
        
        # Mock processor behavior
        mock_batch_encoding = MagicMock()
        # It needs to behave like a dict for items()
        mock_batch_encoding.items.return_value = [("input_features", torch.zeros(1, 100))]
        mock_batch_encoding.__getitem__.side_effect = lambda k: torch.zeros(1, 100) if k == "input_features" else None
        # And satisfy .to()
        mock_batch_encoding.to.return_value = mock_batch_encoding
        
        mock_processor.return_value = mock_batch_encoding
        mock_processor.batch_decode.return_value = ["mocked translation"]
        
        mock_mm.return_value.load_model.return_value = (mock_model, mock_processor)
        
        translator = SeamlessTranslator(test_config)
        return translator, mock_model, mock_processor

def test_translate_audio(mock_translator, tmp_path):
    translator, mock_model, mock_processor = mock_translator
    
    # Create a dummy input file
    input_file = tmp_path / "test.wav"
    input_file.write_text("dummy") # The content doesn't matter if we mock stream_audio
    
    with patch("tool.audio_processor.AudioProcessor.stream_audio") as mock_stream, \
         patch("tool.audio_processor.AudioProcessor.save_audio"):
        # stream_audio should yield (waveform, sample_rate)
        mock_stream.return_value = [(torch.zeros(1, 16000), 16000)]
        
        metadata = translator.translate_audio(input_file, "deu")
        
        assert metadata["status"] == "success"
        assert metadata["target_lang"] == "deu"
        assert "translated_text" in metadata
        assert metadata["translated_text"] == "mocked translation"
        
        # Verify model was called
        assert mock_model.generate.called
        # Verify output file exists (AudioProcessor.save_audio is called)
        assert Path(metadata["target_file"]).parent.exists()

def test_translate_audio_stream(mock_translator):
    translator, mock_model, mock_processor = mock_translator
    # Create a dummy chunk of 16-bit PCM audio (e.g. 10 samples = 20 bytes)
    # Make it non-silent (> 0.01 RMS)
    # Max amplitude is 32767. Half amplitude 16000.
    import struct
    # 10 samples of 16000 amplitude
    dummy_chunk = (struct.pack('<h', 16000) * 10)
    
    # We need to ensure the mocked processor behaves correctly for the streaming call
    # The current mock fixture might need adjustment or we just assume it returns the dict
    # The mocked generate returns (audio, tokens), audio needs to be convertible to numpy
    
    result_audio, result_text = translator.translate_audio_stream(dummy_chunk, "deu")
    
    assert isinstance(result_audio, bytes)
    assert result_text == "mocked translation"
    assert mock_model.generate.called
    assert mock_processor.called
