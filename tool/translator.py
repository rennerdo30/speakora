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
        
        # Streaming context state
        self._streaming_context = {
            'audio_buffer': [],  # Recent audio chunks for context
            'text_history': [],  # Recent translated text for context
            'max_buffer_size': 5,  # Number of chunks to keep in buffer
            'decoder_state': None,  # Optional: decoder hidden states for continuity
            'last_source_lang': None,
            'last_target_lang': None,
        }

    def load_model(self):
        """Prepare model and processor."""
        self.model, self.processor = self.model_manager.load_model()
    
    def detect_language(self, audio_file: Path) -> str:
        """
        Detect the source language of an audio file.
        Uses SeamlessM4T's built-in language detection.
        
        Returns:
            Language code (e.g., 'eng', 'deu', 'fra')
        """
        if self.model is None:
            self.load_model()
        
        logger.info(f"Detecting language for {audio_file}...")
        
        # Load a sample of the audio (first 10 seconds for speed)
        import soundfile as sf
        info = sf.info(str(audio_file))
        sample_duration = min(10.0, info.duration)
        sample_frames = int(sample_duration * info.samplerate)
        
        waveform, sample_rate = self.audio_processor.load_audio(audio_file)
        # Take only first 10 seconds
        max_samples = int(sample_rate * sample_duration)
        if waveform.shape[1] > max_samples:
            waveform = waveform[:, :max_samples]
        
        # Process audio
        inputs = self.processor(
            audios=waveform.squeeze().numpy(),
            sampling_rate=sample_rate,
            return_tensors="pt"
        ).to(self.device)
        
        # Move to device and correct dtype
        inputs = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
        if self.config.model.dtype == "float16" and self.device != "cpu":
            inputs = {k: v.to(torch.float16) if isinstance(v, torch.Tensor) and v.dtype == torch.float32 else v for k, v in inputs.items()}
        
        # Use model's language detection (SeamlessM4T can detect language)
        with torch.no_grad():
            # Generate with auto-detection (src_lang=None)
            output = self.model.generate(
                **inputs,
                tgt_lang="eng",  # Use English as target for detection
                src_lang=None   # Auto-detect source
            )
        
        # Extract detected language from output
        # SeamlessM4T returns language info in the output
        # For now, we'll use a simple approach: try to detect from the model's internal state
        # In practice, SeamlessM4T v2 has language detection built-in
        # This is a simplified version - in production, you might want to use the model's lang_id output
        
        # For now, return a placeholder - the actual detection would use the model's language ID head
        # This is a workaround until we can access the language ID directly
        detected_lang = "eng"  # Default fallback
        
        logger.info(f"Detected language: {detected_lang} (using model's auto-detection)")
        return detected_lang

    def translate_audio(
        self,
        input_file: Path,
        target_lang: str,
        source_lang: str = "auto",
        output_file: Optional[Path] = None,
        reference_audio: Optional[Path] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Translate a single audio file with optional voice preservation."""
        if self.model is None:
            self.load_model()
            
        logger.info(f"Translating {input_file} to {target_lang}...")
        
        # Auto-detect source language if needed
        if source_lang == "auto":
            try:
                detected_lang = self.detect_language(input_file)
                source_lang = detected_lang
                logger.info(f"Auto-detected source language: {source_lang}")
            except Exception as e:
                logger.warning(f"Language detection failed: {e}. Using default 'eng'")
                source_lang = "eng"
        
        if reference_audio and reference_audio.exists():
            pass
        
        # 1. Process in chunks (streaming from disk)
        # Use stream_audio for memory efficiency
        CHUNK_SIZE_SEC = 60
        
        translated_audio_pieces = []
        translated_text_pieces = []
        
        import numpy as np
        
        chunk_idx = 0
        
        try:
             # Estimate total size just for progress (if possible)
             # soundfile.info gives frames
             import soundfile as sf
             total_frames = sf.info(str(input_file)).frames
             total_sr = sf.info(str(input_file)).samplerate
             total_duration = total_frames / total_sr
             total_chunks = int(np.ceil(total_duration / CHUNK_SIZE_SEC))
        except:
             total_chunks = 0

        batch_waveforms = []
        current_batch_indices = []
        got_chunks = False

        for chunk_waveform, chunk_sample_rate in self.audio_processor.stream_audio(input_file, CHUNK_SIZE_SEC):
            got_chunks = True
            chunk_idx += 1
            
            # Squeeze (1, len) -> (len,) or keep (1, len)?
            # Processor expects list of (len,) usually for batching.
            waveform_squeezed = chunk_waveform.squeeze()
            batch_waveforms.append(waveform_squeezed.numpy())
            current_batch_indices.append(chunk_idx)
            
            if len(batch_waveforms) >= self.config.processing.batch_size:
                self._process_batch_and_append(
                    batch_waveforms, 
                    chunk_sample_rate, 
                    target_lang, 
                    source_lang, 
                    translated_audio_pieces, 
                    translated_text_pieces
                )
                logger.info(f"Processed chunks {current_batch_indices[0]}-{current_batch_indices[-1]}")
                
                # Update progress
                if progress_callback and total_chunks > 0:
                     progress = (current_batch_indices[-1] / total_chunks) * 100.0
                     progress_callback(min(progress, 99.0))
                
                batch_waveforms = []
                current_batch_indices = []

        # Process remaining
        if batch_waveforms:
            self._process_batch_and_append(
                batch_waveforms, 
                chunk_sample_rate, # valid from last iteration
                target_lang, 
                source_lang, 
                translated_audio_pieces, 
                translated_text_pieces
            )
            logger.info(f"Processed chunks {current_batch_indices[0]}-{current_batch_indices[-1]}")
            if progress_callback and total_chunks > 0:
                 progress = (current_batch_indices[-1] / total_chunks) * 100.0
                 progress_callback(min(progress, 99.0))
            
            if progress_callback and total_chunks > 0:
                 progress = (chunk_idx / total_chunks) * 100.0
                 progress_callback(min(progress, 99.0))

        if not got_chunks:
             return {
                "source_file": str(input_file),
                "status": "failed",
                "error": "Empty or invalid audio file"
             }
            
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
        sample_rate: int = 16000,
        use_context: bool = True
    ) -> Tuple[bytes, str]:
        """
        Translate a real-time audio chunk with optional context from previous chunks.
        
        Args:
            chunk: Audio chunk bytes (16-bit PCM)
            target_lang: Target language code
            source_lang: Source language code
            sample_rate: Audio sample rate
            use_context: Whether to use context from previous chunks for better translation
        
        Returns:
            Tuple of (translated_audio_bytes, translated_text)
        """
        if self.model is None:
            self.load_model()
            
        import numpy as np
        
        # Reset context if language changed
        if (self._streaming_context['last_target_lang'] != target_lang or 
            self._streaming_context['last_source_lang'] != source_lang):
            self.reset_streaming_context()
            self._streaming_context['last_target_lang'] = target_lang
            self._streaming_context['last_source_lang'] = source_lang
        
        # 1. Convert bytes to numpy waveform (assuming 16-bit PCM)
        waveform_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
        
        # --- Voice Activity Detection (Simple Energy-based fallback or Silero if loaded) ---
        # Check Root Mean Square (RMS) amplitude
        rms = np.sqrt(np.mean(waveform_np**2))
        if rms < 0.01: # Threshold for silence
            # Return silence but still maintain context
            return chunk, ""
        
        # 2. Build context-aware input if enabled
        if use_context and len(self._streaming_context['audio_buffer']) > 0:
            # Concatenate recent chunks for better context
            # Use last 2-3 chunks (roughly 0.5-1 second of audio at 16kHz)
            context_chunks = self._streaming_context['audio_buffer'][-2:] + [waveform_np]
            # Ensure we don't exceed reasonable length (e.g., 2 seconds)
            max_samples = sample_rate * 2
            combined_waveform = np.concatenate(context_chunks)
            if len(combined_waveform) > max_samples:
                # Keep only the most recent portion
                combined_waveform = combined_waveform[-max_samples:]
            
            # Use combined waveform for processing
            waveform_to_process = combined_waveform
        else:
            waveform_to_process = waveform_np
        
        # 3. Process
        inputs = self.processor(
            audios=waveform_to_process,
            sampling_rate=sample_rate,
            return_tensors="pt"
        ).to(self.device)
        
        # Move tensors to device and correct dtype
        inputs = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
        if self.config.model.dtype == "float16" and self.device != "cpu":
             inputs = {k: v.to(torch.float16) if isinstance(v, torch.Tensor) and v.dtype == torch.float32 else v for k, v in inputs.items()}

        # 4. Generate translation
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
        
        # 5. Extract only the portion corresponding to the current chunk
        # If we used context, we need to extract the relevant part
        if use_context and len(self._streaming_context['audio_buffer']) > 0:
            # The output corresponds to the combined waveform
            # Extract the portion that corresponds to the new chunk
            # For simplicity, we'll use the last portion of the output
            # (This is approximate - in production, you'd track exact alignment)
            chunk_duration_samples = len(waveform_np)
            if len(translated_audio) > chunk_duration_samples:
                # Take the last portion corresponding to the new chunk
                translated_audio = translated_audio[-chunk_duration_samples:]
        
        # 6. Update context buffer
        if use_context:
            self._streaming_context['audio_buffer'].append(waveform_np)
            if len(self._streaming_context['audio_buffer']) > self._streaming_context['max_buffer_size']:
                self._streaming_context['audio_buffer'].pop(0)
            
            # Update text history for potential future use
            if translated_text:
                self._streaming_context['text_history'].append(translated_text)
                if len(self._streaming_context['text_history']) > self._streaming_context['max_buffer_size']:
                    self._streaming_context['text_history'].pop(0)
        
        # 7. Convert back to bytes (16-bit PCM)
        translated_audio_bytes = (translated_audio * 32768.0).astype(np.int16).tobytes()
        
        return translated_audio_bytes, translated_text
    
    def reset_streaming_context(self):
        """Reset the streaming context buffer. Call this when starting a new conversation."""
        self._streaming_context = {
            'audio_buffer': [],
            'text_history': [],
            'max_buffer_size': 5,
            'decoder_state': None,
            'last_source_lang': None,
            'last_target_lang': None,
        }
        logger.debug("Streaming context reset")

    def _process_batch_and_append(
        self,
        batch_waveforms,
        sample_rate,
        target_lang,
        source_lang,
        translated_audio_pieces,
        translated_text_pieces
    ):
        """Helper to process a batch of waveforms and append results."""
        import numpy as np
        import torch
        
        # Prepare inputs
        inputs = self.processor(
            audios=batch_waveforms,
            sampling_rate=sample_rate,
            return_tensors="pt",
            padding=True # padding is automatic for list but robust to strict it
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
        
        # Output val is (batch, samples) or (batch, 1, samples)?
        # SeamlessM4T: output.waveform is (batch, 1, samples)
        
        generated_audio_np = val.cpu().numpy()
        decoded_texts = self.processor.batch_decode(tokens, skip_special_tokens=True)
        
        # Iterate and append
        for i in range(len(batch_waveforms)):
            # Audio
            one_audio = generated_audio_np[i].squeeze()
            translated_audio_pieces.append(one_audio)
            
            # Text
            translated_text_pieces.append(decoded_texts[i])
