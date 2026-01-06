# S2ST-Translator

SeamlessM4T v2 Speech-to-Speech Translation System.

## Features
- ✅ Batch Translation
- ✅ Job Management (SQLite)
- ✅ GPU Acceleration (Metal, CUDA)
- ✅ Multi-language support

## Setup
```bash
./setup.sh
```

## Usage
### CLI
```bash
python -m tool.main translate --input sample.wav --target-lang deu
```

### Job Queue
```bash
python -m tool.main job submit --input ./input --target-lang deu
```

## Development
```bash
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
