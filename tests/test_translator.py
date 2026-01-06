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
        mock_processor.return_value = {"input_features": torch.zeros(1, 100)}
        mock_processor.batch_decode.return_value = ["mocked translation"]
        
        mock_mm.return_value.load_model.return_value = (mock_model, mock_processor)
        
        translator = SeamlessTranslator(test_config)
        return translator, mock_model, mock_processor

def test_translate_audio(mock_translator, tmp_path):
    translator, mock_model, mock_processor = mock_translator
    
    # Create a dummy input file
    input_file = tmp_path / "test.wav"
    input_file.write_text("dummy") # AudioProcessor is also mocked/patched or we use a real one with dummy data
    
    with patch("tool.audio_processor.AudioProcessor.load_audio") as mock_load:
        mock_load.return_value = (torch.zeros(1, 16000), 16000)
        
        metadata = translator.translate_audio(input_file, "deu")
        
        assert metadata["status"] == "success"
        assert metadata["target_lang"] == "deu"
        assert "translated_text" in metadata
        assert metadata["translated_text"] == "mocked translation"
        
        # Verify model was called
        assert mock_model.generate.called
        # Verify output file exists (AudioProcessor.save_audio is called)
        assert Path(metadata["target_file"]).parent.exists()

def test_translate_audio_stream_not_implemented(mock_translator):
    translator, _, _ = mock_translator
    with pytest.raises(NotImplementedError):
        translator.translate_audio_stream(b"chunk", "deu")
