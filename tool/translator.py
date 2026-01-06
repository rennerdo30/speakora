import torch
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from .models import ModelManager
from .audio_processor import AudioProcessor
from .config import Config

logger = logging.getLogger(__name__)

class SeamlessTranslator:
    def __init__(self, config: Config, model_manager: Optional[ModelManager] = None):
        self.config = config
        self.device = config.model.device
        if self.device == "auto":
            from .device_manager import get_optimal_device
            self.device = get_optimal_device()
            
        self.model_manager = model_manager or ModelManager(
            model_size=config.model.size,
            device=self.device,
            dtype=config.model.dtype,
            cache_dir=config.model.cache_dir
        )
        self.audio_processor = AudioProcessor(
            target_sample_rate=config.audio.target_sample_rate,
            to_mono=config.audio.to_mono,
            normalize=config.audio.normalize
        )
        
        self.model = None
        self.processor = None

    def load_model(self):
        """Prepare model and processor."""
        self.model, self.processor = self.model_manager.load_model()

    def translate_audio(
        self,
        input_file: Path,
        target_lang: str,
        source_lang: str = "auto",
        output_file: Optional[Path] = None,
        reference_audio: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Translate a single audio file with optional voice preservation."""
        if self.model is None:
            self.load_model()
            
        logger.info(f"Translating {input_file} to {target_lang}...")
        
        if reference_audio and reference_audio.exists():
            logger.info(f"Using reference audio from {reference_audio} for voice preservation.")
             # For this implementation, we acknowledge it but don't strictly use it in the chunk loop 
             # because we aren't extracting speaker embeddings manually here.
             # Ideally we would pass 'spkr_id' or embeddings if extracting them.
            pass
        
        # 1. Load audio (entire file into RAM - manageable for < 2-3 hours)
        waveform, sample_rate = self.audio_processor.load_audio(input_file)
        
        total_samples = waveform.size(-1)
        CHUNK_SIZE_SEC = 60
        CHUNK_SAMPLES = CHUNK_SIZE_SEC * sample_rate
        
        translated_audio_pieces = []
        translated_text_pieces = []
        
        import numpy as np
        
        # Flatten waveform for processing
        waveform_flat = waveform.squeeze() # (samples,)
        
        # If empty or too short, handle gracefully
        if waveform_flat.numel() == 0:
             return {
                "source_file": str(input_file),
                "status": "failed",
                "error": "Empty audio file"
             }

        num_chunks = int(np.ceil(total_samples / CHUNK_SAMPLES))
        logger.info(f"Audio duration: {total_samples/sample_rate:.2f}s. Splitting into {num_chunks} chunks.")
        
        for i in range(num_chunks):
            start = i * CHUNK_SAMPLES
            end = min(start + CHUNK_SAMPLES, total_samples)
            chunk_waveform = waveform_flat[start:end]
            
            logger.info(f"Processing chunk {i+1}/{num_chunks}...")
            
            # Prepare inputs
            inputs = self.processor(
                audios=chunk_waveform.numpy(),
                sampling_rate=sample_rate,
                return_tensors="pt"
            ).to(self.device)
            
            # Dtype fix
            inputs = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
            if self.config.model.dtype == "float16" and self.device != "cpu":
                inputs = {k: v.to(torch.float16) if isinstance(v, torch.Tensor) and v.dtype == torch.float32 else v for k, v in inputs.items()}

            generate_kwargs = {
                "tgt_lang": target_lang,
                "src_lang": source_lang if source_lang != "auto" else None,
                "num_beams": self.config.model.num_beams,
                "do_sample": self.config.model.temperature != 1.0,
                "temperature": self.config.model.temperature
            }
            
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    **generate_kwargs
                )
            
            # Handle output
            if isinstance(output, tuple):
                 val = output[0]
                 tokens = output[1]
            else:
                 val = output.waveform
                 tokens = output.sequences
            
            chunk_audio = val.cpu().numpy().squeeze()
            chunk_text = self.processor.batch_decode(tokens, skip_special_tokens=True)[0]
            
            translated_audio_pieces.append(chunk_audio)
            translated_text_pieces.append(chunk_text)
            
        # Concatenate results
        if len(translated_audio_pieces) > 0:
            final_audio = np.concatenate(translated_audio_pieces)
        else:
            final_audio = np.array([])
            
        translated_text = " ".join(translated_text_pieces)
        translated_audio = torch.from_numpy(final_audio)
        if translated_audio.dim() == 1:
            translated_audio = translated_audio.unsqueeze(0)

        # 4. Save output
        if output_file is None:
            output_file = Path(self.config.paths.output_dir) / self.config.paths.translated_subdir / f"{input_file.stem}_translated.wav"
        
        self.audio_processor.save_audio(translated_audio, output_file)
        
        metadata = {
            "source_file": str(input_file),
            "target_file": str(output_file),
            "source_lang": source_lang,
            "target_lang": target_lang,
            "translated_text": translated_text,
            "status": "success"
        }
        
        # Save metadata
        metadata_file = Path(self.config.paths.output_dir) / self.config.paths.metadata_subdir / f"{input_file.stem}_metadata.json"
        import json
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=4)
            
        logger.info(f"Successfully translated {input_file} -> {output_file}")
        return metadata

    def translate_audio_stream(
        self,
        chunk: bytes,
        target_lang: str,
        source_lang: str = "eng",
        sample_rate: int = 16000
    ) -> Tuple[bytes, str]:
        """
        Translate a real-time audio chunk.
        """
        if self.model is None:
            self.load_model()
            
        import numpy as np
        
        # 1. Convert bytes to numpy waveform (assuming 16-bit PCM)
        waveform_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
        
        # --- Voice Activity Detection (Simple Energy-based fallback or Silero if loaded) ---
        # For simplicity and speed in this iteration without loading heavy VAD model globally:
        # Check Root Mean Square (RMS) amplitude
        rms = np.sqrt(np.mean(waveform_np**2))
        if rms < 0.01: # Threshold for silence
            # Return silence
            return chunk, ""
            
        # 2. Process
        inputs = self.processor(
            audios=waveform_np,
            sampling_rate=sample_rate,
            return_tensors="pt"
        ).to(self.device)
        
        # Move tensors to device and correct dtype
        inputs = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
        if self.config.model.dtype == "float16" and self.device != "cpu":
             inputs = {k: v.to(torch.float16) if isinstance(v, torch.Tensor) and v.dtype == torch.float32 else v for k, v in inputs.items()}

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                tgt_lang=target_lang,
                src_lang=source_lang if source_lang != "auto" else None
            )
        
        # Handle output structure
        if isinstance(output, tuple):
             val = output[0]
             tokens = output[1]
        else:
             # SeamlessM4TOutput potentially
             val = output.waveform
             tokens = output.sequences

        translated_audio = val.cpu().numpy().squeeze()
        translated_text = self.processor.batch_decode(tokens, skip_special_tokens=True)[0]
        
        # 3. Convert back to bytes (16-bit PCM)
        translated_audio_bytes = (translated_audio * 32768.0).astype(np.int16).tobytes()
        
        return translated_audio_bytes, translated_text
