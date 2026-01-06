import click
import os
import sys
from pathlib import Path
import logging
from .config import load_config, Config
from .logger import setup_logger
from .device_manager import get_device_info
from .translator import SeamlessTranslator
from .job_queue import JobQueue, JobStatus

@click.group()
@click.option("--config", type=click.Path(exists=True), help="Path to YAML configuration file.")
@click.option("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR).")
@click.pass_context
def cli(ctx, config, log_level):
    """SeamlessM4T v2 Speech-to-Speech Translation System."""
    config_path = Path(config) if config else None
    cfg = load_config(config_path)
    
    # Override log level if provided
    cfg.logging.level = log_level
    
    # Setup logging
    log_dir = Path(cfg.paths.output_dir) / cfg.paths.logs_subdir
    log_file = log_dir / "app.log"
    setup_logger(
        "tool",
        log_level=cfg.logging.level,
        log_file=log_file if cfg.logging.file.enabled else None,
        console_enabled=cfg.logging.console.enabled
    )
    
    ctx.obj = cfg

@cli.command()
@click.option("--input", required=True, type=click.Path(exists=True), help="Input audio file.")
@click.option("--target-lang", required=True, help="Target language code (e.g., deu, fra, spa).")
@click.option("--source-lang", default="auto", help="Source language code (default: auto).")
@click.pass_obj
def translate(cfg: Config, input, target_lang, source_lang):
    """Run S2ST translation on a single file."""
    from .languages import validate_language
    if not validate_language(target_lang):
        click.echo(f"Error: Unsupported language code '{target_lang}'.", err=True)
        sys.exit(1)

    translator = SeamlessTranslator(cfg)
    try:
        translator.translate_audio(Path(input), target_lang, source_lang)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.pass_obj
def info(cfg: Config):
    """Show system and GPU info."""
    info_dict = get_device_info()
    for key, value in info_dict.items():
        click.echo(f"{key}: {value}")

@cli.command()
@click.option("--model-size", default="large", help="Model size (small, medium, large).")
@click.pass_obj
def download(cfg: Config, model_size):
    """Pre-download models."""
    cfg.model.size = model_size
    translator = SeamlessTranslator(cfg)
    click.echo(f"Downloading model SeamlessM4T v2 {model_size}...")
    translator.load_model()
    click.echo("Download complete.")

@cli.command()
@click.option("--port", default=5000, help="Port to run the GUI on.")
@click.option("--host", default="127.0.0.1", help="Host to run the GUI on.")
@click.pass_obj
def gui(cfg: Config, port, host):
    """Start web GUI dashboard."""
    import uvicorn
    from .api import create_app
    app = create_app(cfg)
    click.echo(f"Starting GUI at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

@cli.command()
@click.option("--num-workers", default=1, help="Number of parallel workers (default: 1).")
@click.pass_obj
def worker(cfg: Config, num_workers):
    """Start background worker processor(s)."""
    from .worker import Worker
    import threading
    
    if num_workers == 1:
        # Single worker mode
        w = Worker(cfg, worker_id="worker-main")
        try:
            w.start()
        except KeyboardInterrupt:
            click.echo("Stopping worker...")
            w.stop()
    else:
        # Multi-worker mode
        workers = []
        threads = []
        
        def worker_thread(worker_id: str):
            w = Worker(cfg, worker_id=worker_id)
            workers.append(w)
            w.start()
        
        click.echo(f"Starting {num_workers} workers...")
        for i in range(num_workers):
            thread = threading.Thread(
                target=worker_thread,
                args=(f"worker-{i+1}",),
                daemon=False
            )
            thread.start()
            threads.append(thread)
        
        try:
            # Wait for all threads
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            click.echo("Stopping all workers...")
            for w in workers:
                w.stop()
            for thread in threads:
                thread.join(timeout=5)

@cli.group()
def job():
    """Job queue management."""
    pass

@job.command(name="submit")
@click.option("--input", required=True, help="Input audio file or directory.")
@click.option("--target-lang", required=True, help="Target language code.")
@click.option("--priority", default=0, type=int, help="Job priority.")
@click.pass_obj
def job_submit(cfg: Config, input, target_lang, priority):
    """Submit a new job to the queue."""
    from .languages import validate_language
    if not validate_language(target_lang):
        click.echo(f"Error: Unsupported language code '{target_lang}'.", err=True)
        return

    db_path = Path(cfg.paths.output_dir) / "jobs.db"
    queue = JobQueue(db_path)
    input_path = Path(input)
    
    if input_path.is_file():
        job_id = queue.enqueue(str(input_path), target_lang, priority=priority)
        click.echo(f"Submitted job: {job_id}")
    elif input_path.is_dir():
        count = 0
        for f in input_path.glob("*.wav"):
            queue.enqueue(str(f), target_lang, priority=priority)
            count += 1
        click.echo(f"Submitted {count} jobs from directory.")
    else:
        click.echo("Invalid input path.", err=True)

@job.command(name="list")
@click.option("--status", help="Filter by status.")
@click.pass_obj
def job_list(cfg: Config, status):
    """List jobs in the queue."""
    db_path = Path(cfg.paths.output_dir) / "jobs.db"
    queue = JobQueue(db_path)
    jobs = queue.list_jobs(status)
    for j in jobs:
        click.echo(f"ID: {j.id} | Status: {j.status} | File: {j.input_file}")

if __name__ == "__main__":
    cli()
