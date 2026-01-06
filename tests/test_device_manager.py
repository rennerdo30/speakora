import torch
import pytest
from tool.device_manager import get_optimal_device, get_device_info
from unittest.mock import patch, MagicMock

def test_get_optimal_device():
    device = get_optimal_device()
    assert device in ["cuda", "mps", "cpu"]
    if torch.cuda.is_available():
        assert device == "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        assert device == "mps"
    else:
        assert device == "cpu"

def test_get_optimal_device_no_mps_attr():
    with patch("torch.cuda.is_available", return_value=False):
        # Mock torch.backends to NOT have "mps"
        mock_backends = MagicMock()
        del mock_backends.mps
        with patch("torch.backends", mock_backends):
            assert get_optimal_device() == "cpu"

def test_get_device_info():
    info = get_device_info()
    assert "platform" in info
    assert "torch_version" in info
    assert "cpu" in info["available_devices"]

def test_get_optimal_device_cuda():
    with patch("torch.cuda.is_available", return_value=True):
        assert get_optimal_device() == "cuda"

def test_get_optimal_device_mps():
    with patch("torch.cuda.is_available", return_value=False):
        with patch("torch.backends.mps.is_available", return_value=True):
            assert get_optimal_device() == "mps"

def test_get_device_info_cuda():
    with patch("torch.cuda.is_available", return_value=True):
        with patch("torch.cuda.device_count", return_value=1):
            with patch("torch.cuda.get_device_name", return_value="NVIDIA RTX"):
                info = get_device_info()
                assert "cuda" in info["available_devices"]
                assert info["cuda_device_name"] == "NVIDIA RTX"

def test_get_device_info_mps():
    with patch("torch.cuda.is_available", return_value=False):
        with patch("torch.backends.mps.is_available", return_value=True):
            info = get_device_info()
            assert "mps" in info["available_devices"]
            assert info["mps_available"] is True
