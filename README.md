<img src="./docs/public/logo.svg" alt="" width="72" height="72" />

# Speakora

Speech-to-speech translation powered by Meta's **SeamlessM4T v2**. Speakora translates spoken
audio from one language into another — optionally keeping the original speaker's voice — and ships
three ways to drive it: a CLI, a web dashboard, and a browser extension that dubs videos as they
play.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Vue 3](https://img.shields.io/badge/vue-3-42b883)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

**Contents** · [Features](#features) · [Installation](#installation) · [Usage](#usage) ·
[Web dashboard](#web-dashboard) · [Docker](#docker-support) · [Configuration](#configuration) ·
[API](#api-endpoints) · [Development](#development) · [Troubleshooting](#troubleshooting)

## Features

- **High-quality S2ST** — SeamlessM4T v2 for translation and speech synthesis in one pass.
- **Expressive mode** — preserves the original speaker's prosody and tone; zero-shot voice
  preservation keeps speaker identity across languages.
- **Three interfaces**
  - **CLI** for scripted and batch processing.
  - **Web dashboard** (Vue 3 + TypeScript) for queueing, monitoring and inspecting jobs.
  - **Browser extension** that overlays translated audio on any playing video.
- **Background workers** — SQLite-backed job queue with pause, resume and checkpoint recovery.
- **Automatic device selection** — CUDA or Apple MPS when available, CPU fallback otherwise.
- **Resource efficient** — smart chunking keeps memory flat on long recordings.
- **Smart streaming** — voice-activity detection skips silence during real-time translation.

## Installation

### Prerequisites

- Python 3.10+
- FFmpeg
- (Optional) NVIDIA GPU with CUDA or Apple Silicon for hardware acceleration.

### Quick Setup (macOS/Linux)

```bash
# Clone the repository
git clone https://github.com/rennerdo30/speakora.git
cd speakora

# Option 1: All-in-one startup (recommended)
# Updates venv, builds frontend, and starts server
./start.sh

# Option 2: Manual setup
# Run setup script (creates venv and installs dependencies)
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### Quick Setup (Windows)

```batch
# Clone the repository
git clone https://github.com/rennerdo30/speakora.git
cd speakora

# Option 1: All-in-one startup (recommended)
# Updates venv, builds frontend, and starts server
start.bat

# Option 2: Manual setup
# Run setup script
setup.bat

# Activate virtual environment
venv\Scripts\activate.bat
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

## Usage

### Using Setup Scripts

**macOS/Linux:**
```bash
# Run any command
./run.sh translate --input audio.wav --target-lang deu
./run.sh gui --port 5000
./run.sh worker --num-workers 2
```

**Windows:**
```batch
run.bat translate --input audio.wav --target-lang deu
run.bat gui --port 5000
run.bat worker --num-workers 2
```

### CLI Mode

```bash
# Single file translation
python -m tool.main translate --input audio.wav --target-lang deu

# Submit job to queue
python -m tool.main job submit --input audio.wav --target-lang fra

# List jobs
python -m tool.main job list

# Pause/Resume job
python -m tool.main job pause --job-id <job_id>
python -m tool.main job resume --job-id <job_id>

# System info
python -m tool.main info

# Pre-download models
python -m tool.main download --model-size large
```

### Web Dashboard

1. **Start the API server:**
   ```bash
   python -m tool.main gui --port 5000 --host 0.0.0.0
   ```

2. **Start background worker(s):**
   ```bash
   # Single worker
   python -m tool.main worker
   
   # Multiple workers (parallel processing)
   python -m tool.main worker --num-workers 4
   ```

3. **Access the dashboard:**
   - Open `http://localhost:5000` in your browser
   - The frontend is served by the FastAPI backend

The dashboard gives you:

- **Live job table** with status badges, progress meters and pause / resume / cancel actions,
  updated over WebSocket and polled as a fallback.
- **System monitor** for GPU memory, CPU, RAM and queue depth, with meters that turn amber and red
  as utilisation climbs.
- **Job details** showing timings, an estimated time remaining, checkpoint history and a searchable
  live log tail.
- **History** with search, status filtering and pagination.
- **Settings** for model, audio, path and logging options.
- **Light and dark themes** — it follows your operating-system preference and remembers your choice.
- **Keyboard and screen-reader support** — visible focus rings, labelled controls, `Esc` to close
  dialogs, and animations that respect `prefers-reduced-motion`.
- **Responsive layout** — the sidebar becomes a top bar and tables stack into cards on phones.

### Browser Extension

1. **Install the extension:**
   - Go to `chrome://extensions/` in Chrome/Edge/Brave
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `extension/` directory

2. **Start the API server:**
   ```bash
   python -m tool.main gui --port 5000
   ```

3. **Use the extension:**
   - Open any video (YouTube, Twitch, Netflix, etc.)
   - Click the extension icon
   - Select source and target languages
   - Click "Start Translation"
   - The translated audio will overlay the original

## Docker Support

### CPU Mode

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### GPU Mode (NVIDIA CUDA)

```bash
# Requires: nvidia-docker2 or Docker with GPU support

# Build and run with GPU
docker-compose -f docker-compose.gpu.yml up -d

# Set number of workers
NUM_WORKERS=4 docker-compose -f docker-compose.gpu.yml up -d
```

### Docker Environment Variables

- `SEAMLESS_DEVICE`: Device to use (`auto`, `cuda`, `cpu`, `mps`)
- `NUM_WORKERS`: Number of parallel workers (default: 1)
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `CUDA_VISIBLE_DEVICES`: GPU device IDs (for multi-GPU setups)

## Configuration

### Configuration File

Create `config/default.yaml` or use environment variables:

```yaml
model:
  size: "large"              # small, medium, large
  device: "auto"             # auto, cuda, mps, cpu
  dtype: "float16"           # float32, float16

translation:
  source_lang: "auto"        # Language code or "auto"
  target_lang: "eng"         # Required language code

audio:
  target_sample_rate: 16000
  normalize: true
  to_mono: true
```

### Environment Variables

```bash
export SEAMLESS_DEVICE=cuda
export SEAMLESS_MODEL_SIZE=large
export LOG_LEVEL=INFO
export CUDA_VISIBLE_DEVICES=0
```

## API Endpoints

The FastAPI backend provides the following endpoints:

- `GET /api/jobs` - List all jobs
- `POST /api/jobs` - Create new job
- `GET /api/jobs/{job_id}` - Get job details
- `PATCH /api/jobs/{job_id}/pause` - Pause job
- `PATCH /api/jobs/{job_id}/resume` - Resume job
- `DELETE /api/jobs/{job_id}` - Cancel job
- `GET /api/jobs/{job_id}/logs` - Get job logs
- `GET /api/jobs/{job_id}/checkpoints` - Get checkpoint history
- `GET /api/system/status` - System status (GPU, CPU, memory)
- `GET /api/stats` - Job statistics
- `WebSocket /ws/jobs/{job_id}` - Real-time job updates
- `WebSocket /api/ws/translate` - Real-time translation streaming

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=tool --cov-report=html --cov-fail-under=100

# Run specific test file
pytest tests/test_translator.py -v

# View coverage report
open htmlcov/index.html
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev          # Vite dev server on :3000, proxies /api to :5000
npm run type-check   # vue-tsc
npm run build        # production bundle into frontend/dist
npm run preview      # serve the production bundle locally
```

The UI is plain CSS — no framework. Colours, spacing, type sizes, radii, durations and z-indexes
are CSS custom properties declared in `frontend/src/index.css`, together with the shared primitives
(`.btn`, `.icon-btn`, `.badge`, `.form-input`, `.alert`, `.meter`, `.data-table`, `.empty-state`,
`.skeleton`). Add a token there rather than hard-coding a value in a component. Non-visual constants
(poll intervals, page sizes, thresholds) live in `frontend/src/constants.ts`.

Themes are driven by `<html data-theme="light|dark">`: the dark palette is the `:root` default and
`[data-theme='light']` overrides the semantic colour tokens. A tiny inline script in `index.html`
applies the stored or system theme before first paint, and `useTheme()` keeps it in sync.

### Code Quality

```bash
# Format code
black tool/ tests/

# Lint code
flake8 tool/ tests/

# Type checking
mypy tool/
```

## Architecture

- **Backend**: FastAPI (Python) with SQLite job queue
- **Frontend**: Vue 3 + TypeScript + Pinia + Vite, styled with plain CSS custom properties
- **Extension**: Manifest v3 with Web Audio API
- **Translation**: SeamlessM4T v2 (Meta)
- **GPU Support**: Metal (macOS), CUDA (Linux/Windows), ROCm/HIP (Linux/Windows)

## Performance

### Benchmarks (M3 Max, 16GB)

| Config | Duration | Time | RTF |
|--------|----------|------|-----|
| Large, float16, S2ST | 60s | ~120s | 2.0x |
| Medium, float16, S2ST | 60s | ~60s | 1.0x |
| Small, float16, S2ST | 60s | ~30s | 0.5x |

### Optimization Tips

- Use `float16` for faster inference (with minimal quality loss)
- Enable multi-worker mode: `--num-workers 4`
- Use GPU acceleration when available
- For long files, use batch processing with job queue

## Troubleshooting

### GPU Not Detected

```bash
# Check device info
python -m tool.main info

# Force CPU mode
export SEAMLESS_DEVICE=cpu
```

### Out of Memory

- Reduce model size: `--model-size medium` or `small`
- Use `float16` instead of `float32`
- Process files in smaller batches

### Extension Not Working

1. Check API server is running: `http://localhost:5000/api/system/status`
2. Check browser console for errors
3. Verify WebSocket connection in Network tab
4. Ensure extension has necessary permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure 100% test coverage
5. Run linting and type checking
6. Submit a pull request

## License

MIT
