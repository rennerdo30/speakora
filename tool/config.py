import os
from pathlib import Path
from typing import Optional, List
import yaml
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

load_dotenv()

class ModelSettings(BaseModel):
    size: str = "large"
    expressive: bool = False
    device: str = "auto"
    dtype: str = "float16"
    cache_dir: str = str(Path("~/.cache/huggingface/hub").expanduser())
    num_beams: int = 5
    temperature: float = 1.0

class TranslationSettings(BaseModel):
    source_lang: str = "auto"
    target_lang: str = "eng"
    task: str = "s2st"
    return_intermediate_text: bool = True

class AudioSettings(BaseModel):
    target_sample_rate: int = 16000
    normalize: bool = True
    to_mono: bool = True

class PathSettings(BaseModel):
    input_dir: str = "./input"
    output_dir: str = "./output"
    translated_subdir: str = "translated"
    metadata_subdir: str = "metadata"
    logs_subdir: str = "logs"

    @property
    def translated_path(self) -> Path:
        return Path(self.output_dir) / self.translated_subdir

    @property
    def metadata_path(self) -> Path:
        return Path(self.output_dir) / self.metadata_subdir

    @property
    def logs_path(self) -> Path:
        return Path(self.output_dir) / self.logs_subdir

class ConsoleLogging(BaseModel):
    enabled: bool = True
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class FileLogging(BaseModel):
    enabled: bool = True
    max_bytes: int = 10485760
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

class LoggingSettings(BaseModel):
    level: str = "INFO"
    console: ConsoleLogging = ConsoleLogging()
    file: FileLogging = FileLogging()
    json_log: bool = False

class ProcessingSettings(BaseModel):
    num_workers: int = 1
    batch_size: int = 1
    skip_existing: bool = True
    dry_run: bool = False
    resume_from_checkpoint: bool = True

class AdvancedSettings(BaseModel):
    use_amp: bool = True
    num_threads: int = 4
    use_torchscript: bool = False
    seed: int = 42

class SecuritySettings(BaseModel):
    api_key: Optional[str] = None

class Config(BaseModel):
    model: ModelSettings = ModelSettings()
    translation: TranslationSettings = TranslationSettings()
    audio: AudioSettings = AudioSettings()
    paths: PathSettings = PathSettings()
    logging: LoggingSettings = LoggingSettings()
    processing: ProcessingSettings = ProcessingSettings()
    advanced: AdvancedSettings = AdvancedSettings()
    security: SecuritySettings = SecuritySettings()

def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from YAML file and environment variables."""
    config_dict = {}
    if config_path and config_path.exists():
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f) or {}

    # Override with environment variables if present
    # This is a simple implementation, pydantic-settings could be used for more robust env handling
    if os.getenv("SEAMLESS_DEVICE"):
        config_dict.setdefault("model", {})["device"] = os.getenv("SEAMLESS_DEVICE")
    if os.getenv("SEAMLESS_MODEL_SIZE"):
        config_dict.setdefault("model", {})["size"] = os.getenv("SEAMLESS_MODEL_SIZE")
    if os.getenv("INPUT_DIR"):
        config_dict.setdefault("paths", {})["input_dir"] = os.getenv("INPUT_DIR")
    if os.getenv("OUTPUT_DIR"):
        config_dict.setdefault("paths", {})["output_dir"] = os.getenv("OUTPUT_DIR")
    if os.getenv("LOG_LEVEL"):
        config_dict.setdefault("logging", {})["level"] = os.getenv("LOG_LEVEL")
    if os.getenv("SEAMLESS_API_KEY"):
        config_dict.setdefault("security", {})["api_key"] = os.getenv("SEAMLESS_API_KEY")

    return Config(**config_dict)
