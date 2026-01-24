# Claude Code Instructions

> **Project:** Speakora - Speech-to-Speech Translation
> **Status:** Production-ready (Phase 1-4 Complete)
> **Last Updated:** January 2026

---

## Quick Reference

- **Specification:** Always check `SPECIFICATION.md` for detailed technical requirements
- **Agent Rules:** See `.agent/rules/general.md` for persistent guidelines
- **This is a GitHub project** - make commits when appropriate

---

## Project Overview

**Speakora** is a production-grade speech-to-speech translation system using Meta's SeamlessM4T v2 model with:

- **CLI Tool** - Batch processing with rich progress output
- **Web Dashboard** - Vue.js frontend with FastAPI backend, drag-and-drop upload
- **Browser Extension** - Real-time video translation (YouTube, Twitch, Netflix)
- **Job Queue** - SQLite-backed with pause/resume and checkpoint recovery
- **Video Support** - Process MP4, MKV, WebM files with audio extraction/re-muxing
- **YouTube Integration** - Download and translate videos/playlists via yt-dlp
- **RunPod Ready** - Optimized Docker deployment for GPU cloud

---

## Architecture

```
video-translate-direct/
├── tool/                    # Core Python package
│   ├── main.py              # CLI entry point (Click)
│   ├── translator.py        # SeamlessM4T S2ST logic
│   ├── config.py            # Pydantic configuration
│   ├── logger.py            # Centralized logging
│   ├── device_manager.py    # GPU/CPU detection + RunPod support
│   ├── audio_processor.py   # Audio I/O (librosa/torchaudio)
│   ├── models.py            # Model loading & caching
│   ├── job_queue.py         # SQLite job queue + Batch management
│   ├── worker.py            # Background job processor + video re-mux
│   ├── api.py               # FastAPI backend + file upload
│   ├── video_processor.py   # Video audio extraction & re-mux
│   ├── youtube_downloader.py # YouTube/playlist download (yt-dlp)
│   └── languages.py         # Language code validation
├── frontend/                # Vue.js 3 + Vite + TypeScript
│   └── src/components/
│       ├── FileUploadZone.vue   # Drag-and-drop upload
│       ├── YouTubeInput.vue     # YouTube URL with preview
│       └── NewJobModal.vue      # Tabbed job creation
├── extension/               # Browser extension (Manifest v3)
├── config/                  # YAML configuration files
├── tests/                   # pytest test suite (100% coverage target)
├── input/                   # Input audio/video files + uploads
└── output/                  # Translated files, logs, job database
```

---

## Development Guidelines

### Code Standards

1. **Production-ready code only** - No experimental or incomplete code
2. **Proper logging** - Use the centralized logger from `tool/logger.py`
3. **100% test coverage** - All new code must have tests
4. **Type hints** - Use Python type hints throughout
5. **Format with Black** - Run `black tool/ tests/` before committing

### Key Technical Details

| Setting | Value | Notes |
|---------|-------|-------|
| Python | 3.10+ | Required for SeamlessM4T |
| Audio Sample Rate | 16000 Hz | SeamlessM4T requirement |
| Default Model | medium (v1) | For RAM compatibility; large (v2) for best quality |
| Supported Formats | WAV, MP3, FLAC, OGG, M4A | Via librosa/torchaudio |
| Database | SQLite | `output/jobs.db` |
| API Port | 5000 | FastAPI + Vue.js served together |

### Model Selection Logic

```
"large"  → facebook/seamless-m4t-v2-large (v2, ~10GB, 24GB+ RAM)
"medium" → facebook/hf-seamless-m4t-medium (v1, ~3.5GB, 16GB+ RAM)
"small"  → facebook/hf-seamless-m4t-medium (v1, same as medium - small doesn't support S2ST)
```

---

## Common Commands

> **Always use `make` commands** - They handle environment setup automatically.

### Make Commands (Primary Interface)

```bash
# Help
make help                     # Show all available commands with examples

# Setup & Installation
make install                  # Install production dependencies
make install-dev              # Install development dependencies
make setup                    # Full setup: venv, deps, frontend build
make download-model           # Download model (MODEL_SIZE=small|medium|large)

# Running Services
make start                    # Start server + worker (Ctrl+C to stop)
make stop                     # Stop all running services
make server                   # Start API server only (PORT=8000)
make server PORT=8080         # Custom port
make worker                   # Start background worker (NUM_WORKERS=1)
make worker NUM_WORKERS=4     # Multiple workers
make info                     # Show system and GPU information

# CLI Translation
make translate FILE=audio.wav TARGET_LANG=deu

# Frontend
make frontend-dev             # Start frontend dev server with hot reload
make frontend-build           # Build frontend for production

# Testing & Quality
make test                     # Run tests
make test-cov                 # Run tests with coverage report
make test-fast                # Run tests without coverage (faster)
make lint                     # Run linter (flake8)
make format                   # Format code with black
make typecheck                # Run type checker (mypy)
make quality                  # Run all quality checks
make pre-commit               # Run all checks before committing

# Docker
make docker-build             # Build Docker image
make docker-up                # Start containers (CPU)
make docker-gpu               # Start with GPU support (NVIDIA)
make docker-runpod            # Build and run RunPod image
make docker-logs              # View container logs
make docker-down              # Stop containers

# Maintenance
make clean                    # Clean build artifacts and cache
make clean-output             # Clean output directory
make clean-cache              # Clean model cache (re-download required)
make db-reset                 # Reset job database
make jobs-list                # List all jobs

# Utilities
make status                   # Check service status
make health                   # Health check
make logs                     # View recent logs
make tail-logs                # Tail logs in real-time
make api-docs                 # Open API documentation in browser
```

### Shell Scripts (Alternative)

```bash
./setup.sh                    # Create venv and install dependencies
./start.sh                    # All-in-one: update deps, build frontend, start
./run.sh translate --input audio.wav --target-lang deu
./run.sh job list
./run.sh info
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/jobs` | Create new translation job |
| GET | `/api/jobs` | List jobs (with filtering) |
| GET | `/api/jobs/{id}` | Job details |
| PATCH | `/api/jobs/{id}/pause` | Pause job |
| PATCH | `/api/jobs/{id}/resume` | Resume job |
| DELETE | `/api/jobs/{id}` | Cancel job |
| POST | `/api/upload` | Upload file (audio/video) |
| POST | `/api/jobs/batch` | Create batch job |
| GET | `/api/batches` | List all batches |
| GET | `/api/batches/{id}` | Batch details |
| POST | `/api/youtube` | Download YouTube & create job |
| GET | `/api/youtube/metadata` | Get video/playlist metadata |
| GET | `/api/system/status` | GPU memory, queue status, model recommendation |
| GET | `/api/stats` | Job statistics |
| WS | `/ws/jobs/{id}` | Real-time job updates |
| WS | `/api/ws/translate` | Real-time streaming translation |

---

## Configuration

Configuration priority (highest to lowest):
1. CLI flags
2. Environment variables
3. `config/default.yaml`
4. Default values in code

Key environment variables:
```bash
SEAMLESS_DEVICE=auto          # auto, cuda, mps, cpu
SEAMLESS_MODEL_SIZE=medium    # small, medium, large
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
```

---

## Logging

- **Console:** Real-time progress with rich formatting
- **File:** Rotating logs in `output/logs/` (10MB max, 5 backups)
- **Format:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

Logger hierarchy:
```python
from tool.logger import setup_logger
logger = setup_logger(__name__)  # e.g., "tool.translator"
```

---

## Logging Guidelines

### Correlation IDs

Every job and API request gets a unique ID that flows through all logs:

```python
# In API middleware - automatically sets correlation ID
# X-Correlation-ID header propagated through request lifecycle

# In worker - set job context for all logs during processing
from tool.logger import set_job_context, clear_job_context

set_job_context(job.id)  # At start of job processing
# ... all logs now include job_id
clear_job_context()      # At end of job processing
```

Logs will include `correlation_id` and `job_id` fields (visible in JSON logs).

### Structured Logging

Use `extra_fields` for structured data that can be parsed programmatically:

```python
logger.info(
    f"Job completed: {job_id}",
    extra={'extra_fields': {
        'job_id': job_id,
        'duration_ms': 1234.5,
        'output_size_mb': 5.2,
    }}
)
```

### Timing Operations

Use the `timed_operation` context manager for automatic timing logs:

```python
from tool.logger import timed_operation

with timed_operation(logger, "Model loading"):
    model.load()
# Logs: "Starting Model loading" and "Completed Model loading in 1234.5ms"

# Access timing data:
with timed_operation(logger, "Translation") as timing:
    do_work()
print(f"Took {timing['duration_ms']}ms")
```

### Log Levels

| Level | Use Case | Examples |
|-------|----------|----------|
| DEBUG | Detailed tracing, chunk progress | Audio loading, checkpoint saves |
| INFO | Standard operations, status changes | Job start/complete, model loaded |
| WARNING | Recoverable issues, fallbacks | GPU OOM fallback to CPU |
| ERROR | Failures requiring attention | Translation failed, invalid input |

### JSON Logging (Production)

Enable structured JSON logging for production:

```yaml
# config/default.yaml
logging:
  json_log: true
```

JSON logs include:
- `timestamp` - ISO 8601 format
- `level` - Log level
- `logger` - Logger name
- `message` - Log message
- `correlation_id` - Request/job correlation ID
- `job_id` - Current job ID (if set)
- `request_id` - Current request ID (if set)
- All `extra_fields` merged into root

---

## Error Handling

The system handles errors gracefully:

- **OOM:** Auto-reduce batch size, fallback to CPU, suggest smaller model
- **GPU Timeout:** Fallback from expressive to standard S2ST
- **Unsupported Format:** Log error, skip file, continue
- **Job Crash:** Mark as FAILED, save error message, recoverable on restart

---

## Git Workflow

- Make commits when changes are complete and tested
- Use conventional commit messages:
  - `feat:` new features
  - `fix:` bug fixes
  - `docs:` documentation changes
  - `refactor:` code restructuring
  - `test:` test additions/changes
  - `chore:` maintenance tasks

---

## Important Files to Check

| File | Purpose |
|------|---------|
| `SPECIFICATION.md` | Complete technical specification |
| `config/default.yaml` | Default configuration |
| `tool/translator.py` | Core translation logic |
| `tool/api.py` | API endpoints |
| `tool/video_processor.py` | Video audio extraction/re-mux |
| `tool/youtube_downloader.py` | YouTube download via yt-dlp |
| `tool/device_manager.py` | GPU detection + model recommendations |
| `tests/conftest.py` | Shared test fixtures |

---

## File Upload Workflow

1. User drags files onto FileUploadZone component
2. Files are uploaded via `POST /api/upload`
3. Video files have audio extracted automatically
4. Job(s) created with `source_type` field set
5. For multiple files, a Batch is created to group jobs
6. Dashboard shows source type badges and batch progress

---

## YouTube Integration

1. User pastes URL in YouTubeInput component
2. Metadata fetched via `GET /api/youtube/metadata`
3. Preview shows title, thumbnail, duration
4. For playlists: shows video count and total duration
5. Submit via `POST /api/youtube` creates job(s)
6. Playlists create batch with one job per video

---

## Video Processing

For video files (MP4, MKV, WebM, AVI, MOV):
1. Audio extracted at 16kHz using FFmpeg
2. Translation performed on extracted audio
3. Translated audio re-muxed back into video container
4. Output: both `_translated.mp4` and `_translated.wav`

---

## RunPod Deployment

```bash
# Build image
docker build -t video-translate:runpod .

# Deploy
docker-compose -f docker-compose.runpod.yml up -d
```

**Auto model selection based on GPU VRAM:**
- 24GB+ VRAM → v2-large (best quality)
- 16GB+ VRAM → v1-medium (good quality)
- <16GB VRAM → v1-medium (compatible)

**RunPod paths:**
- `/runpod-volume/cache/huggingface` - Model cache
- `/runpod-volume/output` - Output files
- `/runpod-volume/input` - Upload directory

---

## Dependencies

Core:
- `torch`, `torchaudio` - Deep learning
- `transformers` - HuggingFace models
- `librosa`, `soundfile` - Audio processing
- `pydantic` - Configuration validation
- `click`, `rich` - CLI interface
- `fastapi`, `uvicorn` - Web API
- `sqlalchemy` - Database ORM
- `yt-dlp` - YouTube download
- `python-multipart`, `aiofiles` - File upload

Development:
- `pytest`, `pytest-cov` - Testing
- `black`, `flake8`, `mypy` - Code quality

---

## Troubleshooting

**GPU not detected:**
```bash
./run.sh info  # Check device detection
export SEAMLESS_DEVICE=cpu  # Force CPU mode
```

**Out of memory:**
```yaml
# config/default.yaml
model:
  size: "medium"  # or "small" for <16GB RAM
```

**Tests failing:**
```bash
pytest -v tests/test_<module>.py  # Run specific test file
pytest --cov=tool --cov-report=html  # Generate coverage report
```

---

## Documentation

- **Always use Mermaid** for diagrams in documentation
- Mermaid is supported in the Starlight docs site
- Avoid external diagram tools or image files when possible

## Contact

- **Issues:** https://github.com/rennerdo30/speakora/issues
- **License:** MIT
