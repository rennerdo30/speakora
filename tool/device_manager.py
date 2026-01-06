import torch
import platform
import logging

logger = logging.getLogger(__name__)

def get_optimal_device() -> str:
    """Detect the best available device (cuda, mps, cpu)."""
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        # Mac with Apple Silicon or AMD GPU
        return "mps"
    return "cpu"

def get_device_info() -> dict:
    """Get information about the system and available devices."""
    info = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "available_devices": ["cpu"]
    }
    
    if torch.cuda.is_available():
        info["available_devices"].append("cuda")
        info["cuda_device_count"] = torch.cuda.device_count()
        info["cuda_device_name"] = torch.cuda.get_device_name(0)
    
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        info["available_devices"].append("mps")
        info["mps_available"] = True
    
    return info
