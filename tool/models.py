import torch
from transformers import AutoProcessor, SeamlessM4Tv2Model
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(
        self,
        model_size: str = "large",
        device: str = "auto",
        dtype: str = "float16",
        cache_dir: Optional[str] = None,
        expressive: bool = False
    ):
        self.model_size = model_size
        self.device = device
        self.dtype = dtype
        self.cache_dir = cache_dir
        self.expressive = expressive
        
        # For expressive mode, we use the standard model but with special handling
        # SeamlessM4T v2 doesn't have a separate expressive model, but we can use
        # reference audio to preserve voice characteristics
        self.model_name = f"facebook/seamless-m4t-v2-{model_size}"
        self.model: Optional[SeamlessM4Tv2Model] = None
        self.processor: Optional[AutoProcessor] = None

    def load_model(self) -> Tuple[SeamlessM4Tv2Model, AutoProcessor]:
        """Load model and processor."""
        if self.model is not None and self.processor is not None:
            return self.model, self.processor

        logger.info(f"Loading model {self.model_name} on {self.device}...")
        
        torch_dtype = torch.float32
        if self.dtype == "float16" and self.device != "cpu":
            torch_dtype = torch.float16
        elif self.dtype == "bfloat16" and self.device != "cpu":
            torch_dtype = torch.bfloat16

        try:
            # Use slow tokenizer (SentencePiece) instead of fast tokenizer (tiktoken)
            # SeamlessM4T v2 uses SentencePiece format which doesn't convert well to tiktoken
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                use_fast=False  # Force use of SentencePiece tokenizer
            )
            self.model = SeamlessM4Tv2Model.from_pretrained(
                self.model_name,
                torch_dtype=torch_dtype,
                cache_dir=self.cache_dir
            ).to(self.device)
            
            logger.info(f"Model {self.model_name} loaded successfully.")
            return self.model, self.processor
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise

    def clear_cache(self):
        """Free up GPU memory."""
        if self.model is not None:
            self.model.cpu()
            del self.model
            self.model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            # torch.mps.empty_cache() # If available in your torch version
            pass
