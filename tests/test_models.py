import pytest
from unittest.mock import patch, MagicMock
import torch
from tool.models import ModelManager

def test_load_model_cached():
    mm = ModelManager()
    mm.model = MagicMock()
    mm.processor = MagicMock()
    model, proc = mm.load_model()
    assert model == mm.model
    assert proc == mm.processor

def test_load_model():
    with patch("transformers.AutoProcessor.from_pretrained") as mock_proc:
        with patch("transformers.SeamlessM4Tv2Model.from_pretrained") as mock_model:
            mm = ModelManager(model_size="small", device="cpu", dtype="float32")
            mm.load_model()
            
            assert mock_proc.called
            assert mock_model.called
            assert mm.model is not None
            assert mm.processor is not None
            
            # Second call should not reload
            mm.load_model()
            assert mock_proc.call_count == 1

def test_load_model_float16_cuda():
    with patch("transformers.AutoProcessor.from_pretrained") as mock_proc:
        with patch("transformers.SeamlessM4Tv2Model.from_pretrained") as mock_model:
            mm = ModelManager(model_size="small", device="cuda", dtype="float16")
            mm.load_model()
            args, kwargs = mock_model.call_args
            assert kwargs["torch_dtype"] == torch.float16

def test_load_model_bfloat16_cuda():
    with patch("transformers.AutoProcessor.from_pretrained") as mock_proc:
        with patch("transformers.SeamlessM4Tv2Model.from_pretrained") as mock_model:
            mm = ModelManager(model_size="small", device="cuda", dtype="bfloat16")
            mm.load_model()
            args, kwargs = mock_model.call_args
            assert kwargs["torch_dtype"] == torch.bfloat16

def test_load_model_error():
    with patch("transformers.AutoProcessor.from_pretrained", side_effect=Exception("Load fail")):
        mm = ModelManager()
        with pytest.raises(Exception):
            mm.load_model()

def test_clear_cache():
    mm = ModelManager(model_size="small", device="cpu")
    mm.model = MagicMock()
    mm.clear_cache()
    assert mm.model is None
    
    with patch("torch.cuda.is_available", return_value=True):
        with patch("torch.cuda.empty_cache") as mock_empty:
            mm.clear_cache()
            assert mock_empty.called

def test_clear_cache_mps():
    mm = ModelManager(model_size="small", device="mps")
    mm.model = MagicMock()
    with patch("torch.backends.mps.is_available", return_value=True):
        mm.clear_cache()
        assert mm.model is None
