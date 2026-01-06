import torch
import torchaudio
import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Tuple, Union, Optional
import logging
import subprocess
import warnings

logger = logging.getLogger(__name__)

def _check_ffmpeg():
    """Check if ffmpeg is available for better audio format support."""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      check=True, 
                      timeout=2)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

# Check ffmpeg availability once at module load
_FFMPEG_AVAILABLE = _check_ffmpeg()
if not _FFMPEG_AVAILABLE:
    logger.warning(
        "ffmpeg not found. Some audio formats (.m4a, .mp3, etc.) may not work properly. "
        "Install ffmpeg for better format support: brew install ffmpeg (macOS) or "
        "sudo apt-get install ffmpeg (Linux)"
    )

class AudioProcessor:
    def __init__(
        self,
        target_sample_rate: int = 16000,
        to_mono: bool = True,
        normalize: bool = True
    ):
        self.target_sample_rate = target_sample_rate
        self.to_mono = to_mono
        self.normalize = normalize

    def stream_audio(
        self, 
        file_path: Union[str, Path], 
        chunk_duration_sec: float = 60.0
    ):
        """
        Yields chunks of preprocessed audio (waveform, sample_rate).
        Reads incrementally from disk to avoid high RAM usage.
        Uses librosa for better format support (including .m4a, .mp3, etc.).
        """
        try:
            # Use librosa to get file info (supports more formats than soundfile)
            import librosa
            # Suppress deprecation warnings from librosa when using audioread fallback
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=FutureWarning, module='librosa')
                warnings.filterwarnings('ignore', category=UserWarning, module='librosa')
                info = librosa.get_duration(path=str(file_path))
                # Get native sample rate by loading a small sample (for duration calculation)
                waveform_sample, native_sr = librosa.load(str(file_path), sr=None, duration=0.1)
            
            # Calculate block size in samples using target_sample_rate
            # (we'll resample everything to target_sample_rate anyway)
            block_size_samples = int(chunk_duration_sec * self.target_sample_rate)
            
            # Use librosa's streaming capability or load in chunks
            # librosa doesn't have direct streaming, so we'll use torchaudio or load in chunks
            try:
                # Try torchaudio first (better for streaming)
                import torchaudio
                waveform, sr = torchaudio.load(str(file_path))
                # Always resample to target_sample_rate (16000 Hz for SeamlessM4T)
                if sr != self.target_sample_rate:
                    resampler = torchaudio.transforms.Resample(sr, self.target_sample_rate)
                    waveform = resampler(waveform)
                    sr = self.target_sample_rate
                
                # Split into chunks
                total_samples = waveform.shape[-1]
                for start_idx in range(0, total_samples, block_size_samples):
                    end_idx = min(start_idx + block_size_samples, total_samples)
                    chunk = waveform[:, start_idx:end_idx]
                    
                    # Process chunk
                    if self.to_mono and chunk.shape[0] > 1:
                        chunk = chunk.mean(dim=0, keepdim=True)
                    
                    # Normalize
                    if self.normalize:
                        max_val = chunk.abs().max()
                        if max_val > 0:
                            chunk = chunk / max_val
                    
                    yield chunk, self.target_sample_rate
            except Exception:
                # Fallback: use librosa to load entire file (less memory efficient but works)
                # Always resample to target_sample_rate (16000 Hz for SeamlessM4T)
                with warnings.catch_warnings():
                    if not _FFMPEG_AVAILABLE:
                        warnings.filterwarnings('ignore', category=FutureWarning, module='librosa')
                    waveform_np, sr = librosa.load(
                        str(file_path),
                        sr=self.target_sample_rate,  # Resample to target rate
                        mono=False
                    )
                
                # Convert to torch tensor
                if waveform_np.ndim == 1:
                    waveform = torch.from_numpy(waveform_np).unsqueeze(0)
                else:
                    waveform = torch.from_numpy(waveform_np)
                
                # Split into chunks
                total_samples = waveform.shape[-1]
                for start_idx in range(0, total_samples, block_size_samples):
                    end_idx = min(start_idx + block_size_samples, total_samples)
                    chunk = waveform[:, start_idx:end_idx]
                    
                    # Process chunk
                    if self.to_mono and chunk.shape[0] > 1:
                        chunk = chunk.mean(dim=0, keepdim=True)
                    
                    # Normalize
                    if self.normalize:
                        max_val = chunk.abs().max()
                        if max_val > 0:
                            chunk = chunk / max_val
                    
                    yield chunk, self.target_sample_rate
                
        except Exception as e:
            logger.error(f"Error streaming audio from {file_path}: {e}")
            raise

    def load_audio(self, file_path: Union[str, Path]) -> Tuple[torch.Tensor, int]:
        """Load and preprocess audio file."""
        # Use librosa as a fallback if torchaudio fails or for better compatibility
        try:
            # We can use librosa for more reliable loading on different platforms
            # Suppress deprecation warnings if ffmpeg is not available
            with warnings.catch_warnings():
                if not _FFMPEG_AVAILABLE:
                    warnings.filterwarnings('ignore', category=FutureWarning, module='librosa')
                waveform_np, sample_rate = librosa.load(
                    str(file_path),
                    sr=self.target_sample_rate,
                    mono=self.to_mono
                )
            
            waveform = torch.from_numpy(waveform_np)
            if waveform.dim() == 1:
                waveform = waveform.unsqueeze(0)
            
            # Normalize if requested
            if self.normalize:
                if waveform.abs().max() > 0:
                    waveform = waveform / waveform.abs().max()
                    
            return waveform, self.target_sample_rate
            
        except Exception as e:
            logger.error(f"Error loading audio file {file_path}: {e}")
            raise

    def save_audio(
        self,
        waveform: torch.Tensor,
        file_path: Union[str, Path],
        sample_rate: Optional[int] = None
    ):
        """Save audio waveform to file."""
        if sample_rate is None:
            sample_rate = self.target_sample_rate
            
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Ensure waveform is (length, channels) for soundfile
            if waveform.dim() == 2:
                # (channels, length) -> (length, channels)
                data = waveform.cpu().numpy().T
            else:
                data = waveform.cpu().numpy()
                
            sf.write(str(file_path), data, sample_rate)
            logger.info(f"Saved audio to {file_path}")
        except Exception as e:
            logger.error(f"Error saving audio file {file_path}: {e}")
            raise
