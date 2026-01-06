import torch
import torchaudio
import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Tuple, Union, Optional
import logging

logger = logging.getLogger(__name__)

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

    def load_audio(self, file_path: Union[str, Path]) -> Tuple[torch.Tensor, int]:
        """Load and preprocess audio file."""
        # Use librosa as a fallback if torchaudio fails or for better compatibility
        try:
            # We can use librosa for more reliable loading on different platforms
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
