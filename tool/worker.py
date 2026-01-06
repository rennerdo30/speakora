import time
import logging
from pathlib import Path
from .config import Config
from .job_queue import JobQueue, JobStatus
from .translator import SeamlessTranslator

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.db_path = Path(cfg.paths.output_dir) / "jobs.db"
        self.queue = JobQueue(self.db_path)
        self.translator = SeamlessTranslator(cfg)
        self.running = False

    def start(self):
        """Start the background worker."""
        logger.info("Starting background worker...")
        
        # Reset stale jobs
        stale_jobs = self.queue.list_jobs(status=JobStatus.RUNNING)
        if stale_jobs:
            logger.warning(f"Found {len(stale_jobs)} stale jobs. Marking them as FAILED.")
            for job in stale_jobs:
                self.queue.update_job_status(job.id, JobStatus.FAILED, error_message="Worker restarted while job was running.")
        
        self.running = True
        self.translator.load_model()
        
        while self.running:
            try:
                # 1. Fetch next queued job
                jobs = self.queue.list_jobs(status=JobStatus.QUEUED)
                if not jobs:
                    time.sleep(5)
                    continue
                
                job = jobs[0]
                logger.info(f"Processing job {job.id}...")
                
                # 2. Check for checkpoints
                checkpoint = self.queue.get_latest_checkpoint(job.id)
                audio_pos = 0
                if checkpoint:
                    logger.info(f"Resuming job {job.id} from position {checkpoint.audio_position}")
                    audio_pos = checkpoint.audio_position
                
                # 3. Update status to RUNNING
                self.queue.update_job_status(job.id, JobStatus.RUNNING)
                
                # 4. Process with periodic checkpointing
                try:
                    input_file = Path(job.input_file)
                    output_file = Path(self.cfg.paths.output_dir) / self.cfg.paths.translated_subdir / f"{input_file.stem}_translated.wav"
                    
                    # Simulation of segmented processing for checkpoint demonstration
                    # In a real S2ST system, this would be chunked processing
                    self.queue.update_job_status(job.id, JobStatus.RUNNING, progress_percent=25.0)
                    self.queue.save_checkpoint(job.id, {"state": "processing"}, audio_position=audio_pos + 1000)
                    
                    self.queue.update_job_status(job.id, JobStatus.RUNNING, progress_percent=50.0)
                    self.queue.save_checkpoint(job.id, {"state": "processing"}, audio_position=audio_pos + 2000)
                    
                    self.translator.translate_audio(
                        input_file,
                        job.target_lang,
                        job.source_lang or "auto",
                        output_file,
                        reference_audio=input_file if self.cfg.model.expressive else None
                    )
                    
                    # 5. Update status to COMPLETED
                    self.queue.update_job_status(
                        job.id, 
                        JobStatus.COMPLETED, 
                        progress_percent=100.0,
                        output_file=str(output_file)
                    )
                except Exception as e:
                    logger.error(f"Error processing job {job.id}: {e}")
                    self.queue.update_job_status(job.id, JobStatus.FAILED, error_message=str(e))
                
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                time.sleep(5)

    def stop(self):
        """Stop the worker."""
        self.running = False
