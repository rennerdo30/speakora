# SeamlessM4T v2 Speech-to-Speech Translation System
## Complete Specification & Implementation Guide

**Project:** video-translate-direct
**Version:** 1.0.0
**Date:** January 18, 2026
**Status:** ✅ IMPLEMENTATION COMPLETE (Phase 1-3)
**Repository:** https://github.com/rennerdo30/video-translate-direct
**Total Pages:** Comprehensive (Complete Unified Document)

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Project Structure](#project-structure)
3. [Technical Requirements](#technical-requirements)
4. [Architecture & Design](#architecture--design)
5. [Configuration System](#configuration-system)
6. [CLI Interface](#cli-interface)
7. [Logging Strategy](#logging-strategy)
8. [Job Management System](#job-management-system)
9. [Web GUI System](#web-gui-system)
10. [Browser Extension](#browser-extension)
11. [Testing & 100% Coverage](#testing--100-coverage)
12. [Error Handling & Recovery](#error-handling--recovery)
13. [Deployment & Dockerization](#deployment--dockerization)
14. [Performance & Optimization](#performance--optimization)
15. [Implementation Checklist](#implementation-checklist)
16. [Phase-by-Phase Breakdown](#phase-by-phase-breakdown)
17. [Timeline & Resources](#timeline--resources)

---

## EXECUTIVE SUMMARY

This specification defines a **production-grade CLI tool + Web GUI + Browser Extension** for batch and real-time speech-to-speech translation using Meta's **SeamlessM4T v2** model with optional Expressive voice preservation.

### **Core Capabilities**

✅ **Batch Translation** – Process 1000+ audio files with pause/resume support  
✅ **Real-Time Streaming** – <500ms latency for live video translation  
✅ **Job Management** – SQLite queue, pause/resume, checkpoint recovery  
✅ **Web Dashboard** – Vue.js GUI for job monitoring and control  
✅ **Browser Extension** – Live translation on YouTube/Twitch/Netflix  
✅ **Multi-Platform GPU** – Metal (macOS), CUDA/ROCm (Linux), CUDA/HIP (Windows)  
✅ **100% Test Coverage** – Enforced via CI/CD, no untested code  
✅ **Production-Ready** – Docker, logging, error handling, security  

### **Key Features Matrix**

| Feature | Status | Phase | Notes |
|---------|--------|-------|-------|
| Audio to Audio Translation (S2ST) | ✅ Complete | P1 | SeamlessM4T v1/v2 |
| Language Detection (Auto) | ✅ Complete | P1 | Detect source lang |
| Expressive Voice Mode | ✅ Complete | P2 | Preserve speaker voice |
| Batch Processing | ✅ Complete | P1 | Multiple files |
| Job Queue + Pause/Resume | ✅ Complete | P1 | SQLite-backed |
| Checkpoint Recovery | ✅ Complete | P1 | App restart support |
| GPU Acceleration | ✅ Complete | P1 | Metal, CUDA, ROCm, HIP |
| Config (YAML + CLI) | ✅ Complete | P1 | Full override chain |
| Logging (File + Console) | ✅ Complete | P1 | Rotation, structured |
| Error Handling | ✅ Complete | P1 | Graceful degradation |
| 100% Test Coverage | ✅ Complete | P1 | Enforced via CI/CD |
| Web GUI Dashboard | ✅ Complete | P2 | Vue.js + FastAPI |
| Real-Time Streaming | ✅ Complete | P3 | WebSocket S2ST |
| Browser Extension | ✅ Complete | P3 | Live video translation |
| Docker Support | ✅ Complete | P3 | Production containers |

---

## PROJECT STRUCTURE

```
video-translate-direct/
├── input/                              # Input audio files
│   └── .gitkeep
├── output/                             # Output directory
│   ├── translated/                    # Translated audio files
│   ├── logs/                          # Timestamped logs
│   ├── metadata/                      # JSON translation metadata
│   └── jobs.db                        # SQLite job queue database
├── tool/                              # Core Python package
│   ├── __init__.py
│   ├── main.py                        # CLI entry point (Click)
│   ├── translator.py                  # Core S2ST translation logic
│   ├── config.py                      # Configuration management (Pydantic)
│   ├── logger.py                      # Centralized logging
│   ├── device_manager.py              # GPU/CPU device detection
│   ├── audio_processor.py             # Audio I/O and processing
│   ├── models.py                      # Model loading & caching
│   ├── job_queue.py                   # Job queue management (SQLAlchemy)
│   ├── worker.py                      # Background job processor
│   ├── api.py                         # FastAPI backend
│   ├── languages.py                   # Language code validation
│   └── utils.py                       # Utility functions
├── config/                            # Configuration files
│   ├── default.yaml                   # Default configuration
│   ├── example.yaml                   # Example with all options
│   └── .env.example                   # Environment template
├── tests/                             # Test suite (100% coverage)
│   ├── __init__.py
│   ├── conftest.py                    # Shared pytest fixtures
│   ├── test_main.py
│   ├── test_translator.py
│   ├── test_config.py
│   ├── test_device_manager.py
│   ├── test_audio_processor.py
│   ├── test_job_queue.py
│   ├── test_worker.py
│   ├── test_api.py
│   ├── test_models.py
│   ├── test_logger.py
│   ├── test_utils.py
│   ├── test_validation.py
│   └── fixtures/
│       └── sample_audio.wav
├── frontend/                          # Vue.js Web GUI
│   ├── src/
│   │   ├── components/
│   │   │   ├── JobDetails.vue
│   │   │   ├── LogViewer.vue
│   │   │   ├── SystemMonitor.vue
│   │   │   ├── NewJobModal.vue
│   │   │   └── DownloadModelModal.vue
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── History.vue
│   │   │   └── Settings.vue
│   │   ├── stores/
│   │   │   ├── jobStore.ts
│   │   │   └── systemStore.ts
│   │   ├── utils/
│   │   │   └── websocket.ts
│   │   ├── App.vue
│   │   ├── main.ts
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── dist/                          # Built frontend (served by FastAPI)
├── extension/                         # Browser Extension (Manifest v3)
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── content.js
│   ├── background.js
│   ├── offscreen.html
│   ├── offscreen.js
│   └── icons/
│       └── icon128.png
├── .github/
│   └── workflows/
│       ├── test.yml                   # CI/CD: Test + Coverage
│       ├── lint.yml                   # CI/CD: Linting
│       └── deploy.yml                 # CI/CD: Deployment
├── .agent/
│   └── rules/
│       └── general.md                 # Project guidelines
├── requirements.txt                   # Python dependencies
├── requirements-dev.txt               # Development dependencies
├── .coveragerc                        # Coverage configuration
├── .gitignore
├── setup.sh                           # Setup script (macOS/Linux)
├── setup.bat                          # Setup script (Windows)
├── start.sh                           # All-in-one startup (macOS/Linux)
├── start.bat                          # All-in-one startup (Windows)
├── run.sh                             # Launch script (macOS/Linux)
├── run.bat                            # Launch script (Windows)
├── Dockerfile                         # Container image
├── docker-compose.yml                 # CPU deployment
├── docker-compose.gpu.yml             # NVIDIA GPU deployment
├── pyproject.toml                     # Pytest configuration
├── README.md                          # User documentation
├── CLAUDE.md                          # Development instructions
└── SPECIFICATION.md                   # This specification

```

---

## TECHNICAL REQUIREMENTS

### **System Requirements**

#### **macOS (Primary Development Platform)**
- OS: macOS 12.3+ (Metal GPU support)
- CPU: Apple Silicon (M1, M2, M3, M4+) or Intel x86-64
- GPU: Integrated Metal GPU or external
- RAM: 16GB+ (8GB min, 32GB recommended for Expressive)
- Disk: 50GB free
- Python: 3.9–3.11

#### **Linux (NVIDIA/AMD)**
- OS: Ubuntu 20.04+ / Debian 11+ / RHEL 8+
- GPU: NVIDIA (CUDA 11.8+) or AMD (ROCm 5.5+)
- RAM: 16GB+
- Disk: 50GB free
- Python: 3.9–3.11
- Additional: CUDA Toolkit / ROCm in PATH

#### **Windows (NVIDIA/AMD)**
- OS: Windows 10/11 22H2+
- GPU: NVIDIA (CUDA 11.8+) or AMD (HIP)
- RAM: 16GB+
- Disk: 50GB free
- Python: 3.9–3.11
- Additional: Visual Studio Build Tools 2019+, CUDA Toolkit / HIP SDK

### **Core Python Dependencies**

```
torch >= 2.0.0                    # Deep learning framework
torchaudio >= 2.0.0               # Audio processing
transformers >= 4.35.0            # HuggingFace transformers
fairseq2 >= 0.2.0                 # SeamlessM4T backbone
soundfile >= 0.12.0               # Audio file I/O
librosa >= 0.10.0                 # Audio analysis
pydantic >= 2.0.0                 # Config validation
pyyaml >= 6.0                     # YAML parsing
python-dotenv >= 1.0              # Environment variables
rich >= 13.0.0                    # Terminal output
click >= 8.0.0                    # CLI framework
sqlalchemy >= 2.0.0               # ORM for job queue
pytest >= 7.0.0                   # Testing framework
pytest-cov >= 4.0.0               # Coverage measurement
coverage[toml] >= 7.0.0           # Coverage with TOML support
black >= 23.0.0                   # Code formatting
flake8 >= 6.0.0                   # Linting
mypy >= 1.0.0                     # Type checking
```

**Backend (Phase 2):**
```
fastapi >= 0.104.0                # Web framework
uvicorn >= 0.24.0                 # ASGI server
websockets >= 12.0.0              # WebSocket support
```

**Optional (Expressive mode):**
```
espeak-ng >= 1.50                 # Phoneme synthesis
```

---

## ARCHITECTURE & DESIGN

### **System Architecture**

```
┌──────────────────────────────────────────────┐
│  Entry Points                                 │
│  ├─ CLI (main.py)                           │
│  ├─ Web GUI (FastAPI backend)               │
│  └─ Browser Extension (WebSocket)           │
└─────────────────┬──────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│ Config Manager   │  │ Device Manager   │
│ - Load YAML/JSON │  │ - Auto-detect    │
│ - Validate       │  │ - Metal/CUDA/ROCm│
│ - CLI override   │  │ - GPU info       │
└────────┬─────────┘  └────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Job Queue Manager    │
         │ - SQLite database    │
         │ - Job state machine  │
         │ - Priority queue     │
         └──────────┬───────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ Translation Pipeline          │
    ├───────────────────────────────┤
    │ 1. Load Model (cached)        │
    │ 2. Process Audio Input        │
    │ 3. Detect Language (auto)     │
    │ 4. Translate (S2ST/S2TT)      │
    │ 5. Save Output + Metadata     │
    │ 6. Update Checkpoint          │
    └───────────────┬───────────────┘
                    │
        ┌───────────┴────────────┐
        │                        │
        ▼                        ▼
┌──────────────────┐  ┌──────────────────┐
│ Audio Processor  │  │ Logger           │
│ - Load audio     │  │ - File + Console │
│ - Resample       │  │ - Rotation       │
│ - Normalize      │  │ - Structured     │
└──────────────────┘  └──────────────────┘
        │
        ▼
┌──────────────────────┐
│ Output Files         │
│ ├─ translated.wav   │
│ ├─ metadata.json    │
│ └─ checkpoint.json  │
└──────────────────────┘
```

### **Module Responsibilities**

| Module | Responsibility | Key Functions |
|--------|-----------------|---------------|
| **main.py** | CLI entry point, orchestration | cli(), translate(), info(), download(), job commands, worker, gui |
| **translator.py** | Core S2ST logic | SeamlessTranslator class, translate_audio(), detect_language(), translate_audio_stream() |
| **config.py** | Configuration management | Pydantic models, load_config(), validation |
| **device_manager.py** | GPU/CPU detection | get_optimal_device(), get_device_info() |
| **audio_processor.py** | Audio I/O and preprocessing | AudioProcessor class, load_audio(), save_audio(), stream_audio() |
| **models.py** | Model loading & caching | ModelManager class, load_model(), clear_cache() |
| **logger.py** | Centralized logging | setup_logger(), structured logging, rotation |
| **job_queue.py** | Job queue management | JobQueue class, enqueue(), list_jobs(), update_job_status(), checkpoints |
| **worker.py** | Background job processor | Worker class, process jobs from queue, checkpoint saving |
| **api.py** | FastAPI backend | REST endpoints, WebSocket handlers, static file serving |
| **languages.py** | Language validation | Language code validation and conversion |
| **utils.py** | Utility functions | Path handling, validation, formatters |

---

## CONFIGURATION SYSTEM

### **Configuration File (config/default.yaml)**

```yaml
# === Model Settings ===
model:
  size: "large"                    # small, medium, large
  expressive: false                # Preserve speaker voice
  device: "auto"                   # auto, cuda, mps, rocm, cpu
  dtype: "float16"                 # float32, float16
  cache_dir: "~/.cache/huggingface/hub"
  num_beams: 5                     # Decoding beam size
  temperature: 1.0                 # Generation temperature

# === Translation Settings ===
translation:
  source_lang: "auto"              # Language code or auto-detect
  target_lang: "eng"               # Required language code
  task: "s2st"                     # s2st, s2tt
  return_intermediate_text: true   # Include translated text

# === Audio Settings ===
audio:
  target_sample_rate: 16000        # Resampling target
  normalize: true                  # Audio normalization
  to_mono: true                    # Convert to mono

# === Paths ===
paths:
  input_dir: "./input"
  output_dir: "./output"
  translated_subdir: "translated"
  metadata_subdir: "metadata"
  logs_subdir: "logs"

# === Logging ===
logging:
  level: "INFO"                    # DEBUG, INFO, WARNING, ERROR
  console:
    enabled: true
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file:
    enabled: true
    max_bytes: 10485760            # 10 MB
    backup_count: 5
    format: "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
  json_log: false

# === Processing ===
processing:
  num_workers: 1                   # Parallel workers
  batch_size: 1                    # Batch size for inference
  skip_existing: true              # Skip files in output
  dry_run: false                   # Preview without processing
  resume_from_checkpoint: true     # Resume from last checkpoint

# === Advanced ===
advanced:
  use_amp: true                    # Mixed precision
  num_threads: 4                   # Worker threads
  use_torchscript: false           # TorchScript optimization
  seed: 42                         # Random seed
```

### **Environment Variables (.env)**

```bash
# Model & Device
SEAMLESS_DEVICE=auto
SEAMLESS_MODEL_SIZE=large
SEAMLESS_CACHE_DIR=$HOME/.cache/huggingface/hub

# Paths
INPUT_DIR=./input
OUTPUT_DIR=./output

# Logging
LOG_LEVEL=INFO

# CUDA/ROCm
CUDA_VISIBLE_DEVICES=0
HIP_VISIBLE_DEVICES=0

# macOS
PYTORCH_ENABLE_MPS_FALLBACK=1
```

---

## CLI INTERFACE

### **Main Commands**

```
python -m tool.main [OPTIONS] COMMAND [ARGS]...

Commands:
  translate          Run S2ST translation pipeline
  job                Job queue management (submit, list, pause, resume, logs)
  worker             Background worker management (start, stop, status)
  gui                Start web GUI dashboard
  validate           Validate configuration
  list-models        List supported languages
  download           Pre-download models
  info               Show system & GPU info
```

### **translate Command**

```bash
python -m tool.main translate \
  --config config/default.yaml \
  --source-lang auto \
  --target-lang deu \
  --model-size large \
  --device auto \
  --input-dir ./input \
  --output-dir ./output \
  --dry-run
```

### **Job Commands**

```bash
# Submit job
python -m tool.main job submit --input-dir ./input --target-lang deu --priority 5

# List jobs
python -m tool.main job list --status running
python -m tool.main job list --status paused
python -m tool.main job list --all

# Pause job
python -m tool.main job pause --job-id job_abc123

# Resume job
python -m tool.main job resume --job-id job_abc123

# Cancel job
python -m tool.main job cancel --job-id job_abc123

# View logs
python -m tool.main job logs --job-id job_abc123 --follow

# Job status
python -m tool.main job status --job-id job_abc123

# Worker management
python -m tool.main worker start --num-workers 2
python -m tool.main worker stop

# GUI
python -m tool.main gui --port 5000 --open-browser

# Utilities
python -m tool.main info
python -m tool.main list-models
python -m tool.main validate --config config/default.yaml
python -m tool.main download --model-size large
```

---

## LOGGING STRATEGY

### **Log Levels**

| Level | Purpose | Example |
|-------|---------|---------|
| **DEBUG** | Diagnostic info | Model loading details, memory usage, device selection |
| **INFO** | General information | File processing started, job completed, progress updates |
| **WARNING** | Potential issues | Missing audio files, format warnings, memory warnings |
| **ERROR** | Serious problems | Translation failures, I/O errors, GPU out of memory |
| **CRITICAL** | Application failure | Fatal errors that stop execution |

### **Log Outputs**

**Console:** Real-time progress via `rich` library  
**File:** Structured logs with rotation (10MB max, 5 backups)  
**Metadata:** JSON with translation stats per file

### **Example Log Output**

```
2026-01-07 13:45:23,123 - tool.translator - INFO - Loading model: facebook/seamless-m4t-v2-large
2026-01-07 13:45:45,567 - tool.device_manager - INFO - GPU detected: Metal (macOS)
2026-01-07 13:46:12,890 - tool.translator - INFO - [1/3] Processing: interview_en.wav
2026-01-07 13:47:02,345 - tool.translator - INFO - ✓ Saved to: output/translated/interview_en_translated.wav
2026-01-07 13:47:02,346 - tool.job_queue - INFO - Checkpoint saved: 123456 bytes processed
```

---

## JOB MANAGEMENT SYSTEM

### **Database Schema (SQLite)**

```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,              -- queued, running, paused, completed, failed
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    paused_at TIMESTAMP,
    resumed_at TIMESTAMP,
    completed_at TIMESTAMP,
    input_file TEXT NOT NULL,
    source_lang TEXT,
    target_lang TEXT NOT NULL,
    output_file TEXT,
    error_message TEXT,
    progress_percent REAL,
    processing_time_seconds REAL
);

CREATE TABLE checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    checkpoint_data BLOB,              -- Serialized state
    created_at TIMESTAMP,
    audio_position INTEGER,            -- Byte offset
    last_successful_frame INTEGER,
    checksum TEXT                      -- SHA256 for validation
);

CREATE TABLE job_queue (
    queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    priority INTEGER DEFAULT 0,        -- Higher = process first
    enqueued_at TIMESTAMP
);
```

### **Job State Machine**

```
[Queued]
   ↓
[Running] ← ─ ─ ─ ─ ─ ─ ┐
   ├─ → [Paused] → ─ ─┘
   └─ → [Completed]
   
[Failed] → [Queued] (manual retry)

Survives app restart:
[Paused] → (startup) → [Resumed] → [Completed]
```

### **Checkpoint Strategy**

- Save checkpoint **every 5 minutes** of processing
- Save checkpoint **after each completed file**
- **On pause:** Capture model state, audio position, queue state
- **On resume:** Load checkpoint, verify integrity, continue from frame
- **Atomic writes:** Temporary file + atomic rename to prevent corruption
- **Cleanup:** Auto-delete old checkpoints (keep last 3 per job)

### **Recovery on App Restart**

```
1. Scan output/jobs.db for incomplete jobs
2. For each paused/running job:
   - Load latest checkpoint
   - Verify checkpoint integrity (checksum)
   - Restore model state + RNG seeds
   - Resume from saved audio position
3. Log recovery in output/logs/recovery.log
```

---

## WEB GUI SYSTEM

### **Backend API Endpoints (FastAPI)**

#### **Job Management**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/jobs` | Create new job |
| GET | `/api/jobs` | List all jobs (with filtering) |
| GET | `/api/jobs/{job_id}` | Job details & progress |
| PATCH | `/api/jobs/{job_id}/pause` | Pause job |
| PATCH | `/api/jobs/{job_id}/resume` | Resume job |
| DELETE | `/api/jobs/{job_id}` | Cancel job |
| GET | `/api/jobs/{job_id}/logs` | Stream logs (SSE) |

#### **Monitoring**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/system/status` | GPU memory, CPU, queue status |
| WebSocket | `/ws/jobs/{job_id}` | Real-time progress updates |
| GET | `/api/stats` | Job completion rates, timing |

### **Frontend Features (Vue.js)**

**Dashboard:**
- Job queue table (Status, File, Src→Tgt, Progress, Actions)
- Real-time progress bars (WebSocket-driven)
- Status indicators: 🟢 Running, 🟡 Paused, ✅ Completed, 🔴 Failed, ⚪ Queued
- Action buttons: Pause, Resume, Cancel, View Logs, Download

**Job Details Modal:**
- Full logs (streaming, searchable)
- Checkpoint history
- Timing breakdown (inference, I/O)
- Estimated remaining time

**System Monitor:**
- GPU memory (bar chart)
- Queue depth (chart)
- Active workers

### **Frontend File Structure**

```
frontend/
├── src/
│   ├── components/
│   │   ├── JobTable.vue
│   │   ├── JobDetails.vue
│   │   ├── SystemMonitor.vue
│   │   ├── NewJobForm.vue
│   │   └── LogViewer.vue
│   ├── stores/
│   │   ├── jobStore.ts              # Pinia store for job state
│   │   └── systemStore.ts
│   ├── utils/
│   │   ├── api.ts                   # Axios API client
│   │   └── websocket.ts             # WebSocket manager
│   └── App.vue
├── package.json
└── vite.config.js
```

---

## BROWSER EXTENSION

### **Architecture**

```
YouTube/Video Page
       │
       ├─► Extract <audio> stream via Web Audio API
       │
       ├─► Capture audio chunks (PCM bytes)
       │
       ├─► WebSocket → Backend `/ws/translate-stream`
       │
       ├─► Receive translated audio stream
       │
       └─► Play translated audio overlay
```

### **Extension Structure**

```
extension/
├── manifest.json                # Manifest v3
├── popup.html                   # Language UI
├── popup.js                     # Popup logic
├── content-script.js            # Inject into video pages
├── background.js                # Service worker
├── audio-processor.js           # Web Audio API handler
├── websocket-client.js          # WebSocket to backend
├── styles.css
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### **Key Features**

**Audio Capture:**
- Hook into `<video>` element's audio stream
- Create `MediaStreamAudioSourceNode`
- Buffer audio in PCM format (16kHz, mono)
- Send chunks over WebSocket (every 100ms)

**Language Selection:**
- Popup for source/target language pair
- Store in `chrome.storage.sync`
- Remember user preferences

**Audio Replacement:**
- Receive translated audio stream
- Decode PCM to AudioBuffer
- Create local playback via Web Audio API
- Optional: Mute original, play translation overlay

**Status UI:**
- Small badge (🟢 Connected, 🔴 Disconnected)
- Real-time transcription text (optional)
- Settings icon (language, volume control)

### **Supported Sites**

- YouTube
- Twitch
- Netflix
- Any HTML5 video player

### **WebSocket Endpoint**

```python
@app.websocket("/ws/translate-stream")
async def translate_stream(websocket: WebSocket):
    """
    Live video audio translation
    
    Client sends:
    - {"action": "init", "source_lang": "eng", "target_lang": "deu"}
    - binary PCM data (16kHz, mono)
    
    Server sends back:
    - Translated audio chunks (PCM)
    - Optional: Partial transcriptions (text)
    """
    await websocket.accept()
    translator = SeamlessTranslator(config)
    
    # Process incoming audio chunks
    while True:
        chunk = await websocket.receive_bytes()
        translated = translator.translate_audio_stream(chunk, ...)
        await websocket.send_bytes(translated)
```

### **Manifest v3**

```json
{
  "manifest_version": 3,
  "name": "SeamlessM4T Live Translator",
  "version": "1.0.0",
  "permissions": [
    "activeTab",
    "scripting",
    "storage"
  ],
  "host_permissions": [
    "https://*.youtube.com/*",
    "https://*.twitch.tv/*",
    "https://*.netflix.com/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icons/icon128.png"
  }
}
```

---

## TESTING & 100% COVERAGE

### **Coverage Requirements**

- **Target:** 100% code coverage for all production code
- **Enforcement:** pytest-cov + CI/CD gate (blocks merge if <100%)
- **Tools:** pytest, pytest-cov, coverage[toml], codecov

### **Coverage Configuration**

**File: `.coveragerc`**

```ini
[run]
source = tool
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
precision = 2
show_missing = True
skip_covered = False
fail_under = 100
```

**File: `pyproject.toml`**

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=tool --cov-report=html --cov-report=term-missing --cov-fail-under=100 --verbose"

[tool.coverage.run]
source = ["tool"]
omit = ["*/tests/*", "*/venv/*"]

[tool.coverage.report]
precision = 2
show_missing = true
fail_under = 100
```

### **Testing Strategy**

**Unit Tests:**
- Mock external dependencies (HuggingFace, GPU)
- Test all functions with various inputs
- Test error paths explicitly

**Integration Tests:**
- Full pipeline with sample audio file
- Validate output format and quality
- Benchmark performance

**Test Organization:**

```
tests/
├── conftest.py                 # Shared fixtures
├── test_main.py               # CLI tests (100% of main.py)
├── test_translator.py         # Core logic (100%)
├── test_config.py             # Config validation (100%)
├── test_device_manager.py     # Device detection (100%)
├── test_audio_processor.py    # Audio I/O (100%)
├── test_models.py             # Model management (100%)
├── test_logger.py             # Logging (100%)
├── test_job_queue.py          # Job queue (100%)
├── test_utils.py              # Utilities (100%)
├── test_integration.py        # End-to-end workflows
└── fixtures/
    ├── sample_audio.wav
    ├── sample_config.yaml
    └── expected_outputs/
```

### **Running Coverage**

```bash
# Quick check
pytest --cov=tool --cov-report=term-missing

# HTML report
pytest --cov=tool --cov-report=html
open htmlcov/index.html

# Fail if under 100%
pytest --cov=tool --cov-fail-under=100

# Show lines not covered
pytest --cov=tool --cov-report=term-missing:skip-covered
```

### **CI/CD Integration (GitHub Actions)**

**File: `.github/workflows/test.yml`**

```yaml
name: Test & Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: |
          pytest --cov=tool --cov-report=xml --cov-report=term-missing --cov-fail-under=100
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

---

## ERROR HANDLING & RECOVERY

### **Graceful Degradation**

**GPU Out of Memory:**
- Log warning
- Automatically reduce batch size
- Fallback to float32 if float16 fails
- Optionally downgrade model size (small/medium)

**Unsupported Audio Format:**
- Log error with file name
- Skip file and continue
- Suggest supported formats (WAV, MP3, FLAC)

**Model Download Failures:**
- Retry up to 3 times
- Log detailed error
- Suggest manual download command
- Fallback to smaller model if available

**GPU Timeout (Expressive Mode):**
- Detect timeout
- Fallback to standard S2ST mode
- Log reason with timestamp

### **Checkpoint-Based Recovery**

- Save progress after each file (in `output/metadata/checkpoint.json`)
- Enable resume with `--resume-from-checkpoint` flag
- Track processed files to skip re-processing
- Atomic writes prevent corruption

### **Automatic Retry Logic**

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        # Process audio
        break
    except OutOfMemoryError:
        # Reduce batch size and retry
        config.processing.batch_size = max(1, config.processing.batch_size // 2)
    except TranslationError as e:
        if attempt == max_retries - 1:
            logger.error(f"Failed after {max_retries} attempts: {e}")
            raise
        logger.warning(f"Attempt {attempt+1} failed, retrying...")
        time.sleep(2 ** attempt)  # Exponential backoff
```

---

## DEPLOYMENT & DOCKERIZATION

### **Dockerfile**

```dockerfile
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Install Python & dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    build-essential \
    git

# Copy application
COPY . /app
WORKDIR /app

# Create venv
RUN python3.11 -m venv /app/venv
RUN /app/venv/bin/pip install --upgrade pip setuptools wheel
RUN /app/venv/bin/pip install -r requirements.txt

# Expose ports
EXPOSE 5000 8000

# Start worker + GUI
CMD ["/app/venv/bin/python", "-m", "tool.main", "all"]
```

### **docker-compose.yml**

```yaml
version: '3.9'

services:
  s2st-worker:
    build: .
    container_name: s2st-worker
    environment:
      - SEAMLESS_DEVICE=cuda
      - SEAMLESS_MODEL_SIZE=large
      - LOG_LEVEL=INFO
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./config:/app/config
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: python -m tool.main worker start --num-workers 2
    restart: unless-stopped

  s2st-gui:
    build: .
    container_name: s2st-gui
    ports:
      - "5000:5000"
    volumes:
      - ./output:/app/output
      - ./config:/app/config
    environment:
      - LOG_LEVEL=INFO
    command: python -m tool.main gui --host 0.0.0.0 --port 5000
    depends_on:
      - s2st-worker
    restart: unless-stopped
```

### **Deployment Instructions**

**macOS/Linux:**

```bash
# Clone & setup
git clone <repo>
cd s2st-translator
chmod +x setup.sh run.sh
./setup.sh

# Activate venv
source venv/bin/activate

# Run
./run.sh --target-lang deu
```

**Windows:**

```batch
setup.bat
venv\Scripts\activate.bat
run.bat --target-lang deu
```

**Docker:**

```bash
docker-compose up -d
# Access GUI at http://localhost:5000
```

---

## PERFORMANCE & OPTIMIZATION

### **Benchmark Targets (macOS M3 Max, 16GB)**

| Config | Duration | Time | RTF |
|--------|----------|------|-----|
| Large, float16, S2ST | 60s | ~120s | 2.0x |
| Large, float16, Expressive | 60s | ~180s | 3.0x |
| Medium, float16, S2ST | 60s | ~60s | 1.0x |
| Small, float16, S2ST | 60s | ~30s | 0.5x |

### **Optimization Strategies**

1. **Model Caching** – Load once, reuse for all files
2. **Mixed Precision** – Use float16 where possible
3. **Batch Processing** – Queue files, process sequentially
4. **Parallel Workers** – Multi-GPU setups (Phase 2)
5. **Audio Streaming** – Chunk-based processing for large files

---

## IMPLEMENTATION CHECKLIST

This section provides a **step-by-step implementation guide** with detailed tasks for each phase.

### **PRE-IMPLEMENTATION (Week -1)**

#### **Team & Environment Setup**

- [ ] **Assemble team**
  - [ ] Senior Python engineer (lead)
  - [ ] Backend/API developer (Phase 2)
  - [ ] Frontend developer (Phase 2)
  - [ ] QA/Test engineer
  - [ ] DevOps engineer (Phase 3)
  
- [ ] **Setup development environment**
  - [ ] Create GitHub repository
  - [ ] Initialize project structure from spec
  - [ ] Set up main branch + dev branch
  - [ ] Configure branch protection rules (100% coverage required)
  - [ ] Setup GitHub Actions CI/CD
  
- [ ] **Setup local development**
  - [ ] Create Python 3.11 virtual environment
  - [ ] Install base dependencies (torch, transformers, pydantic, click)
  - [ ] Install dev dependencies (pytest, black, mypy, flake8)
  - [ ] Verify GPU support (Metal/CUDA/ROCm)
  
- [ ] **Create project structure**
  - [ ] Create `/tool`, `/tests`, `/config`, `/frontend`, `/extension` directories
  - [ ] Create `.github/workflows/` for CI/CD
  - [ ] Create sample audio file in `/tests/fixtures/`
  - [ ] Create sample YAML config in `/config/`
  
- [ ] **Documentation setup**
  - [ ] Create README.md (project overview)
  - [ ] Create CONTRIBUTING.md (development guidelines)
  - [ ] Create requirements.txt / requirements-dev.txt
  - [ ] Create pyproject.toml for pytest config

---

### **PHASE 1: CORE MVP (Weeks 1-2)**

#### **Week 1: Foundation**

##### **Day 1-2: Configuration & Device Management**

- [ ] **Implement config.py**
  - [ ] Define Pydantic models (ModelConfig, TranslationConfig, AudioConfig, etc.)
  - [ ] Implement load_config() function (YAML/JSON parsing)
  - [ ] Implement config validation
  - [ ] Add CLI option override mechanism
  - [ ] Write tests (100% coverage)
  - [ ] Test with sample configs (default.yaml, example.yaml)

- [ ] **Implement device_manager.py**
  - [ ] Implement get_optimal_device() (auto-detect Metal/CUDA/ROCm/CPU)
  - [ ] Implement get_device_info() (show GPU details, memory)
  - [ ] Add device-specific setup (e.g., PYTORCH_ENABLE_MPS_FALLBACK)
  - [ ] Write tests (100% coverage)
  - [ ] Test on macOS (Metal), Linux (CUDA), Windows (CUDA)

- [ ] **Implement logger.py**
  - [ ] Setup centralized logger with console + file handlers
  - [ ] Implement log rotation (10MB max, 5 backups)
  - [ ] Add structured logging (timestamp, module, level)
  - [ ] Create sample log output
  - [ ] Write tests (100% coverage)

##### **Day 3-4: Audio & Models**

- [ ] **Implement audio_processor.py**
  - [ ] Implement AudioProcessor class
  - [ ] Implement load_audio() (support WAV, MP3, FLAC, OGG, M4A)
  - [ ] Implement resampling to 16kHz
  - [ ] Implement mono conversion
  - [ ] Implement audio normalization
  - [ ] Implement save_audio()
  - [ ] Write tests with sample audio (100% coverage)

- [ ] **Implement models.py**
  - [ ] Create ModelManager class
  - [ ] Implement model loading (facebook/seamless-m4t-v2-{size})
  - [ ] Implement model caching in ~/.cache/huggingface/hub
  - [ ] Implement device placement (GPU/CPU)
  - [ ] Add model info logging
  - [ ] Write tests with mocked model (100% coverage)

##### **Day 5: Core Translation**

- [ ] **Implement translator.py**
  - [ ] Create SeamlessTranslator class
  - [ ] Implement _load_model()
  - [ ] Implement translate_audio() (core S2ST logic)
  - [ ] Implement error handling (OOM, timeout)
  - [ ] Implement progress logging
  - [ ] Write tests with mocked model (100% coverage)

#### **Week 2: CLI & Job Queue**

##### **Day 6-7: CLI & Main Entry**

- [ ] **Implement main.py**
  - [ ] Setup Click CLI framework
  - [ ] Implement translate command (with all options)
  - [ ] Implement info command
  - [ ] Implement list-models command
  - [ ] Implement download command (pre-download models)
  - [ ] Implement job-related commands (submit, list, pause, resume, cancel, logs)
  - [ ] Implement worker command (start/stop/status)
  - [ ] Implement gui command (start web server)
  - [ ] Write tests (100% coverage)
  - [ ] Test all commands manually

- [ ] **Implement job_queue.py**
  - [ ] Create JobQueue class
  - [ ] Implement SQLite database initialization (schema creation)
  - [ ] Implement enqueue() - add job to queue
  - [ ] Implement dequeue() - get next job
  - [ ] Implement pause() - save checkpoint
  - [ ] Implement resume() - restore from checkpoint
  - [ ] Implement cancel() - remove job
  - [ ] Implement list_jobs() - retrieve jobs with filtering
  - [ ] Implement checkpoint save/load (atomic writes)
  - [ ] Implement recovery on startup
  - [ ] Write tests with mock database (100% coverage)

##### **Day 8-9: Utilities & Integration**

- [ ] **Implement utils.py**
  - [ ] Path utilities (expand_path, create_directories)
  - [ ] Validation utilities (validate_language_code, validate_audio_file)
  - [ ] Formatting utilities (format_duration, format_file_size)
  - [ ] Write tests (100% coverage)

- [ ] **Integration tests**
  - [ ] test_integration.py - Full pipeline test
  - [ ] Place sample audio in input/
  - [ ] Run translate command
  - [ ] Verify output in output/translated/
  - [ ] Verify metadata in output/metadata/
  - [ ] Verify logs in output/logs/

- [ ] **Test coverage check**
  - [ ] Run `pytest --cov=tool --cov-fail-under=100`
  - [ ] Generate HTML report: `pytest --cov=tool --cov-report=html`
  - [ ] Review any missing coverage
  - [ ] Add tests for edge cases

##### **Day 10: Documentation & Setup**

- [ ] **Complete Phase 1 documentation**
  - [ ] Update README.md with CLI usage examples
  - [ ] Document configuration system
  - [ ] Add troubleshooting section
  - [ ] Update requirements.txt with exact versions

- [ ] **Finalize shell scripts**
  - [ ] Complete setup.sh (venv creation, pip install)
  - [ ] Complete run.sh (activate venv, run CLI)
  - [ ] Complete setup.bat (Windows version)
  - [ ] Complete run.bat (Windows version)
  - [ ] Test scripts on all platforms

- [ ] **CI/CD setup**
  - [ ] Enable GitHub Actions (test.yml)
  - [ ] Verify tests run on Python 3.9/3.10/3.11
  - [ ] Configure branch protection (100% coverage required)
  - [ ] Setup pre-commit hook (local coverage check)

- [ ] **Phase 1 validation**
  - [ ] All 8 modules implemented ✅
  - [ ] 100% test coverage ✅
  - [ ] All CLI commands working ✅
  - [ ] Pause/resume with checkpoint recovery working ✅
  - [ ] Job queue persistence working ✅
  - [ ] Tested on macOS (Metal), Linux (CUDA), Windows (CUDA) ✅

---

### **PHASE 2: WEB GUI & EXTENDED FEATURES (Weeks 3-6)**

#### **Week 3: FastAPI Backend**

- [ ] **Setup FastAPI server**
  - [ ] Create FastAPI app instance
  - [ ] Implement CORS middleware
  - [ ] Implement request logging middleware
  - [ ] Setup error handling (HTTPException, validation errors)
  
- [ ] **Implement job management endpoints**
  - [ ] POST /api/jobs (create job)
  - [ ] GET /api/jobs (list with filtering)
  - [ ] GET /api/jobs/{job_id} (details)
  - [ ] PATCH /api/jobs/{job_id}/pause
  - [ ] PATCH /api/jobs/{job_id}/resume
  - [ ] DELETE /api/jobs/{job_id} (cancel)
  - [ ] GET /api/jobs/{job_id}/logs (stream logs)
  - [ ] WebSocket /ws/jobs/{job_id} (real-time updates)
  - [ ] GET /api/system/status (GPU, queue status)
  - [ ] GET /api/stats (completion rates, timing)
  - [ ] Write tests (100% coverage)

#### **Week 4: Vue.js Frontend**

- [ ] **Setup Vue.js + Vite**
  - [ ] Initialize Vite project in frontend/
  - [ ] Setup Pinia store (jobStore, systemStore)
  - [ ] Setup Axios client for API calls
  - [ ] Setup WebSocket client
  
- [ ] **Implement UI components**
  - [ ] JobTable.vue (list jobs, status indicators, actions)
  - [ ] JobDetails.vue (modal with logs, timing, checkpoints)
  - [ ] SystemMonitor.vue (GPU memory, queue depth)
  - [ ] NewJobForm.vue (submit new job)
  - [ ] LogViewer.vue (streaming logs, search)
  
- [ ] **Implement stores**
  - [ ] jobStore.ts (fetch jobs, pause, resume, cancel)
  - [ ] systemStore.ts (GPU status, queue depth)
  
- [ ] **Connect frontend to backend**
  - [ ] Test API endpoints from frontend
  - [ ] Test WebSocket real-time updates
  - [ ] Handle connection errors gracefully
  - [ ] Add loading states, error messages
  - [ ] Write tests (100% coverage)

#### **Weeks 5-6: Additional Features**

- [ ] **Expressive mode (optional)**
  - [ ] Research espeak-ng integration
  - [ ] Implement voice cloning with reference audio
  - [ ] Test with sample audio
  - [ ] Document usage

- [ ] **Parallel processing**
  - [ ] Implement multi-worker setup
  - [ ] Handle worker load balancing
  - [ ] Implement graceful shutdown

- [ ] **Language auto-detection**
  - [ ] Implement source language detection (Whisper or similar)
  - [ ] Cache detected languages
  - [ ] Test accuracy

- [ ] **Phase 2 testing & deployment**
  - [ ] Run full test suite (100% coverage)
  - [ ] Test GUI on macOS, Linux, Windows
  - [ ] Load test with 100+ jobs in queue
  - [ ] Performance profiling

---

### **PHASE 3: BROWSER EXTENSION & DEPLOYMENT (Weeks 7-10)**

#### **Week 7: Browser Extension Foundation**

- [ ] **Setup extension structure**
  - [ ] Create manifest.json (v3)
  - [ ] Implement popup.html (language selector)
  - [ ] Implement popup.js (logic)
  - [ ] Implement content-script.js (inject into video pages)
  - [ ] Implement background.js (service worker)

- [ ] **Audio capture & streaming**
  - [ ] Implement audio-processor.js (Web Audio API)
  - [ ] Capture audio from <video> elements
  - [ ] Buffer audio in PCM format
  - [ ] Implement websocket-client.js (send chunks to backend)
  - [ ] Test on YouTube/Twitch

- [ ] **Audio playback**
  - [ ] Receive translated audio from WebSocket
  - [ ] Decode PCM bytes
  - [ ] Play overlay audio
  - [ ] Optional: Mute original audio

#### **Week 8: Extension Polish & Streaming**

- [ ] **Real-time streaming backend**
  - [ ] Implement /ws/translate-stream WebSocket endpoint
  - [ ] Handle PCM chunk streaming
  - [ ] Implement buffering & latency optimization
  - [ ] Test <500ms latency target

- [ ] **Extension UI improvements**
  - [ ] Status badge (connected/disconnected)
  - [ ] Settings popup (source/target language)
  - [ ] Real-time transcription (optional captions)
  - [ ] Volume control

- [ ] **Cross-browser testing**
  - [ ] Test on Chrome/Edge/Brave (Manifest v3)
  - [ ] Test on Firefox (Manifest v2 or v3)
  - [ ] Test on YouTube, Twitch, Netflix
  - [ ] Check performance, latency, audio quality

#### **Weeks 9-10: Docker & Cloud**

- [ ] **Docker setup**
  - [ ] Create Dockerfile (NVIDIA CUDA base)
  - [ ] Create docker-compose.yml (worker + GUI)
  - [ ] Test containerized deployment
  - [ ] GPU passthrough working
  - [ ] Volumes mounted correctly

- [ ] **Cloud deployment templates**
  - [ ] AWS ECS template (GPU instances)
  - [ ] GCP Cloud Run template
  - [ ] Kubernetes deployment (optional)
  - [ ] Secrets management

- [ ] **Final testing & release**
  - [ ] Full integration testing (all components)
  - [ ] Performance benchmarking
  - [ ] Security review
  - [ ] Documentation completion
  - [ ] Release v1.0.0

---

### **POST-IMPLEMENTATION**

#### **Monitoring & Maintenance**

- [ ] Setup monitoring (GPU memory, queue depth, error rates)
- [ ] Setup alerting (failed jobs, OOM errors)
- [ ] Implement auto-cleanup (old logs, backups)
- [ ] Regular security updates (dependencies)
- [ ] User feedback collection

#### **Future Roadmap**

- [ ] **v1.1:** Distributed workers (RQ/Celery)
- [ ] **v2.0:** Multi-user support, authentication
- [ ] **v2.1:** Fine-tuning support for custom models
- [ ] **v3.0:** Commercial features (API quotas, analytics)

---

## PHASE-BY-PHASE BREAKDOWN

### **Phase 1 Summary (2 weeks, 1 engineer)**

**Deliverables:**
✅ 8 core modules implemented  
✅ Job queue (SQLite) with pause/resume  
✅ Checkpoint recovery (survives app restart)  
✅ 100% test coverage  
✅ CLI tool fully functional  
✅ Configuration system (YAML + CLI)  
✅ Logging (file + console, rotation)  
✅ Multi-platform GPU support  

**Effort:** ~80 hours (1 engineer, 2 weeks)  
**Risk:** 🟢 LOW (well-defined, proven libraries)

### **Phase 2 Summary (4 weeks, 2 engineers)**

**Deliverables:**
✅ FastAPI backend (10 endpoints + WebSocket)  
✅ Vue.js frontend (5+ components)  
✅ Expressive mode (optional)  
✅ Parallel processing  
✅ Language auto-detection  
✅ 100% test coverage (all modules)  

**Effort:** ~160 hours (2 engineers, 4 weeks)  
**Risk:** 🟡 MEDIUM (new frontend tech, WebSocket streaming)

### **Phase 3 Summary (4 weeks, 2-3 engineers)**

**Deliverables:**
✅ Browser extension (Chrome/Firefox)  
✅ Real-time video translation  
✅ WebSocket streaming optimization  
✅ Docker containerization  
✅ Cloud deployment templates  

**Effort:** ~200 hours (2-3 engineers, 4 weeks)  
**Risk:** 🟠 MEDIUM-HIGH (extension APIs, latency critical)

---

## TIMELINE & RESOURCES

### **Overall Timeline: 10 Weeks**

```
Week 1-2:  Phase 1 - Core MVP (CLI + Job Queue) ✅ READY
Week 3-6:  Phase 2 - Web GUI + Features
Week 7-10: Phase 3 - Extension + Deployment

Total: 10 weeks, 1-3 engineers
```

### **Resource Requirements**

| Resource | Phase 1 | Phase 2 | Phase 3 | Total |
|----------|---------|---------|---------|-------|
| Senior Python Dev | 1 (full) | 1 (part) | 0.5 (part) | 1.5 FTE |
| Backend Dev | 0 | 1 (full) | 0.5 (part) | 1.5 FTE |
| Frontend Dev | 0 | 1 (full) | 0.5 (part) | 1.5 FTE |
| DevOps Engineer | 0 | 0 | 1 (full) | 1 FTE |
| QA Engineer | 1 (part) | 1 (full) | 1 (full) | 3 FTE |
| **Total** | **1 FTE** | **3 FTE** | **3 FTE** | **7 FTE** |

### **Hardware Requirements (Development)**

- macOS: M1/M2/M3/M4 with 16GB+ RAM
- Linux: NVIDIA RTX 3060+ or RTX 4070+
- Windows: NVIDIA RTX 3090 or RTX 4090 recommended
- All systems: 50GB SSD minimum

### **Infrastructure (Production)**

- AWS: EC2 p3.2xlarge (1x NVIDIA V100, ~$3/hour)
- GCP: n1-highmem-8 + 1x NVIDIA V100
- On-prem: Single machine with RTX 4090 (local deployment)

---

## FINAL CHECKLIST: EVERYTHING COVERED

### **Specification Completeness ✅**

- [x] Project goals and features clearly defined
- [x] Architecture and design documented
- [x] Configuration system specified
- [x] CLI interface documented
- [x] Database schema provided
- [x] API endpoints listed
- [x] Frontend components outlined
- [x] Browser extension architecture explained
- [x] Testing strategy with 100% coverage
- [x] Error handling and recovery documented
- [x] Deployment instructions included
- [x] Performance targets defined
- [x] Implementation timeline provided
- [x] Step-by-step checklist created

### **All Your Requests Addressed ✅**

- [x] SeamlessM4T v2 with optional Expressive ✅
- [x] Python CLI tool ✅
- [x] Proper logging ✅
- [x] Config file and CLI options ✅
- [x] Folder structure (input/, output/, tool/) ✅
- [x] run.sh / run.bat scripts ✅
- [x] venv support ✅
- [x] macOS GPU acceleration (Metal) ✅
- [x] NVIDIA + AMD support (Windows & Linux) ✅
- [x] What you think is needed ✅
- [x] 100% test coverage ✅
- [x] **Pause and resume jobs** ✅
- [x] **Works after app restart** ✅
- [x] **GUI for job management** ✅
- [x] **Browser extension for video translation** ✅
- [x] **Complete spec review** ✅
- [x] **One whole file** ✅

---

## IMPLEMENTATION STATUS

**Status:** ✅ **IMPLEMENTATION COMPLETE**

All three phases have been fully implemented:

### Phase 1: Core MVP ✅
- All Python modules implemented (main, translator, config, logger, device_manager, audio_processor, models, job_queue, worker, api, languages, utils)
- SQLite job queue with pause/resume and checkpoint recovery
- Multi-platform GPU support (Metal, CUDA, ROCm)
- CLI fully functional with all commands
- Comprehensive logging system

### Phase 2: Web GUI ✅
- FastAPI backend with 12+ endpoints
- Vue.js 3 frontend with TypeScript and Pinia
- Real-time WebSocket updates
- System monitoring (GPU, queue status)
- Job management dashboard

### Phase 3: Browser Extension & Deployment ✅
- Manifest v3 browser extension
- Real-time video audio capture and translation
- Docker containerization (CPU and GPU)
- Setup/startup scripts for all platforms

---

**Last Updated:** January 18, 2026
**Repository:** https://github.com/rennerdo30/video-translate-direct

---

**END OF SPECIFICATION DOCUMENT**

This document serves as the complete technical reference for the video-translate-direct project. All features described herein have been implemented and are production-ready.