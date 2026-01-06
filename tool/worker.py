import time
import logging
import threading
import signal
from pathlib import Path
from typing import Optional
from .config import Config
from .job_queue import JobQueue, JobStatus
from .translator import SeamlessTranslator

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self, cfg: Config, worker_id: Optional[str] = None):
        self.cfg = cfg
        self.worker_id = worker_id or f"worker-{threading.get_ident()}"
        self.db_path = Path(cfg.paths.output_dir) / "jobs.db"
        self.queue = JobQueue(self.db_path)
        self.translator = SeamlessTranslator(cfg)
        self.running = False
        self.current_job_id: Optional[str] = None

    def start(self):
        """Start the background worker."""
        logger.info(f"Starting background worker {self.worker_id}...")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Reset stale jobs (only on first worker startup)
        if self.worker_id == "worker-main":
            stale_jobs = self.queue.list_jobs(status=JobStatus.RUNNING)
            if stale_jobs:
                logger.warning(f"Found {len(stale_jobs)} stale jobs. Marking them as FAILED.")
                for job in stale_jobs:
                    self.queue.update_job_status(job.id, JobStatus.FAILED, error_message="Worker restarted while job was running.")
        
        self.running = True
        self.translator.load_model()
        
        import time as time_module
        last_checkpoint_time = time_module.time()
        CHECKPOINT_INTERVAL = 300  # 5 minutes
        
        while self.running:
            try:
                # 1. Fetch next queued job
                jobs = self.queue.list_jobs(status=JobStatus.QUEUED)
                if not jobs:
                    time.sleep(5)
                    continue
                
                job = jobs[0]
                self.current_job_id = job.id
                logger.info(f"[{self.worker_id}] Processing job {job.id}...")
                
                # 2. Check for checkpoints
                checkpoint = self.queue.get_latest_checkpoint(job.id)
                audio_pos = 0
                if checkpoint:
                    logger.info(f"[{self.worker_id}] Resuming job {job.id} from position {checkpoint.audio_position}")
                    audio_pos = checkpoint.audio_position
                
                # 3. Update status to RUNNING
                self.queue.update_job_status(job.id, JobStatus.RUNNING)
                start_time = time_module.time()
                
                # 4. Process with periodic checkpointing
                try:
                    input_file = Path(job.input_file)
                    output_file = Path(self.cfg.paths.output_dir) / self.cfg.paths.translated_subdir / f"{input_file.stem}_translated.wav"
                    
                    def progress_callback(progress: float):
                        self.queue.update_job_status(job.id, JobStatus.RUNNING, progress_percent=progress)
                        
                        # Save checkpoint every 5 minutes
                        current_time = time_module.time()
                        if current_time - last_checkpoint_time >= CHECKPOINT_INTERVAL:
                            try:
                                self.queue.save_checkpoint(job.id, {"progress": progress}, audio_pos)
                                last_checkpoint_time = current_time
                                logger.debug(f"[{self.worker_id}] Checkpoint saved for job {job.id}")
                            except Exception as e:
                                logger.warning(f"[{self.worker_id}] Failed to save checkpoint: {e}")

                    # Determine reference audio for expressive mode
                    reference_audio = None
                    if hasattr(job, 'expressive') and job.expressive:
                        if hasattr(job, 'reference_audio') and job.reference_audio:
                            reference_audio = Path(job.reference_audio)
                        else:
                            # Use input file as reference if no separate reference provided
                            reference_audio = input_file
                    
                    self.translator.translate_audio(
                        input_file,
                        job.target_lang,
                        job.source_lang or "auto",
                        output_file,
                        reference_audio=reference_audio,
                        progress_callback=progress_callback
                    )
                    
                    # Calculate processing time
                    processing_time = time_module.time() - start_time
                    
                    # 5. Update status to COMPLETED
                    self.queue.update_job_status(
                        job.id, 
                        JobStatus.COMPLETED, 
                        progress_percent=100.0,
                        output_file=str(output_file),
                        processing_time_seconds=processing_time
                    )
                    logger.info(f"[{self.worker_id}] Job {job.id} completed in {processing_time:.2f}s")
                    
                except KeyboardInterrupt:
                    logger.info(f"[{self.worker_id}] Interrupted, pausing job {job.id}...")
                    self.queue.update_job_status(job.id, JobStatus.PAUSED)
                    self.running = False
                    break
                except Exception as e:
                    logger.error(f"[{self.worker_id}] Error processing job {job.id}: {e}")
                    self.queue.update_job_status(job.id, JobStatus.FAILED, error_message=str(e))
                
                self.current_job_id = None
                
            except Exception as e:
                logger.error(f"[{self.worker_id}] Worker loop error: {e}")
                time.sleep(5)
        
        logger.info(f"[{self.worker_id}] Worker stopped")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"[{self.worker_id}] Received signal {signum}, shutting down gracefully...")
        if self.current_job_id:
            logger.info(f"[{self.worker_id}] Pausing current job {self.current_job_id}...")
            self.queue.update_job_status(self.current_job_id, JobStatus.PAUSED)
        self.running = False

    def stop(self):
        """Stop the worker gracefully."""
        logger.info(f"[{self.worker_id}] Stopping worker...")
        if self.current_job_id:
            self.queue.update_job_status(self.current_job_id, JobStatus.PAUSED)
        self.running = False
