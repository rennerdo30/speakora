# Claude Code Instructions

> **Project:** SeamlessM4T v2 Speech-to-Speech Translation System
> **Status:** Production-ready (Phase 1-3 Complete)
> **Last Updated:** January 2026

---

## Quick Reference

- **Specification:** Always check `SPECIFICATION.md` for detailed technical requirements
- **Agent Rules:** See `.agent/rules/general.md` for persistent guidelines
- **This is a GitHub project** - make commits when appropriate

---

## Project Overview

A production-grade speech-to-speech translation system using Meta's SeamlessM4T v2 model with:

- **CLI Tool** - Batch processing with rich progress output
- **Web Dashboard** - Vue.js frontend with FastAPI backend
- **Browser Extension** - Real-time video translation (YouTube, Twitch, Netflix)
- **Job Queue** - SQLite-backed with pause/resume and checkpoint recovery

---

## Architecture

```
video-translate-direct/
├── tool/                    # Core Python package
│   ├── main.py              # CLI entry point (Click)
│   ├── translator.py        # SeamlessM4T S2ST logic
│   ├── config.py            # Pydantic configuration
│   ├── logger.py            # Centralized logging
│   ├── device_manager.py    # GPU/CPU detection (Metal/CUDA/ROCm)
│   ├── audio_processor.py   # Audio I/O (librosa/torchaudio)
│   ├── models.py            # Model loading & caching
│   ├── job_queue.py         # SQLite job queue with ORM
│   ├── worker.py            # Background job processor
│   ├── api.py               # FastAPI backend
│   └── languages.py         # Language code validation
├── frontend/                # Vue.js 3 + Vite + TypeScript
├── extension/               # Browser extension (Manifest v3)
├── config/                  # YAML configuration files
├── tests/                   # pytest test suite (100% coverage target)
├── input/                   # Input audio files
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

```bash
# Setup
./setup.sh                    # Create venv and install dependencies
./start.sh                    # All-in-one: update deps, build frontend, start server

# CLI Translation
./run.sh translate --input audio.wav --target-lang deu

# Job Management
./run.sh job submit --input audio.wav --target-lang fra
./run.sh job list
./run.sh job pause --job-id <id>
./run.sh job resume --job-id <id>

# Background Processing
./run.sh worker --num-workers 2

# Web GUI
./run.sh gui --port 5000

# System Info
./run.sh info
./run.sh download --model-size medium

# Testing
pytest --cov=tool --cov-report=term-missing --cov-fail-under=100
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
| GET | `/api/system/status` | GPU memory, queue status |
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
| `tests/conftest.py` | Shared test fixtures |

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

## Contact

- **Issues:** https://github.com/rennerdo30/video-translate-direct/issues
- **License:** MIT
