from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List, Optional, Dict
import asyncio
import logging
import uuid
import time
from collections import defaultdict
from pydantic import BaseModel
from .config import Config
from .job_queue import JobQueue, JobStatus, Job, Checkpoint
from .translator import SeamlessTranslator

logger = logging.getLogger(__name__)

class JobCreate(BaseModel):
    input_file: str
    target_lang: str
    source_lang: str = "auto"
    priority: int = 0
    expressive: bool = False
    reference_audio: Optional[str] = None

def create_app(cfg: Config) -> FastAPI:
    app = FastAPI(title="S2ST Translator API")
    
    # Enhanced CORS - restrict origins in production
    allowed_origins = ["*"]  # In production, set to specific domains
    if cfg.security.api_key:
        # If API key is set, we can be more restrictive
        allowed_origins = ["http://localhost:5173", "http://localhost:5000", "http://127.0.0.1:5173", "http://127.0.0.1:5000"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    from fastapi import status
    from fastapi.responses import JSONResponse
    
    # Rate limiting storage (in production, use Redis or similar)
    rate_limit_store: Dict[str, List[float]] = defaultdict(list)
    RATE_LIMIT_REQUESTS = 100  # requests per window
    RATE_LIMIT_WINDOW = 60  # seconds

    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        # Skip security for docs and static files
        if request.url.path in ["/docs", "/openapi.json", "/", "/favicon.ico"]:
            return await call_next(request)
        
        # Rate limiting
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        if client_ip in rate_limit_store:
            rate_limit_store[client_ip] = [
                t for t in rate_limit_store[client_ip] 
                if current_time - t < RATE_LIMIT_WINDOW
            ]
        
        # Check rate limit
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Record request
        rate_limit_store[client_ip].append(current_time)
        
        # API Key authentication
        if cfg.security.api_key:
            api_key = request.headers.get("X-API-KEY")
            if api_key != cfg.security.api_key:
                logger.warning(f"Unauthorized API access attempt from IP: {client_ip}, path: {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or missing API Key"}
                )
        
        # Log security-relevant requests
        if request.method in ["POST", "DELETE", "PATCH"]:
            logger.info(f"Security: {request.method} {request.url.path} from {client_ip}")
        
        return await call_next(request)

    db_path = Path(cfg.paths.output_dir) / "jobs.db"
    queue = JobQueue(db_path)
    translator = SeamlessTranslator(cfg)
    
    # Store translator instances per WebSocket connection for context isolation
    active_streams: Dict[str, SeamlessTranslator] = {}

    @app.get("/api/jobs")
    async def list_jobs(status: Optional[str] = None):
        return queue.list_jobs(status)

    @app.post("/api/jobs")
    async def create_job(job_data: JobCreate):
        from .languages import validate_language
        if not validate_language(job_data.target_lang):
            raise HTTPException(status_code=400, detail=f"Unsupported target language: {job_data.target_lang}")
        
        input_path = Path(job_data.input_file)
        if not input_path.exists():
            raise HTTPException(status_code=400, detail=f"Input file does not exist: {job_data.input_file}")

        # Validate reference audio if provided
        reference_audio_path = None
        if job_data.reference_audio:
            reference_audio_path = Path(job_data.reference_audio)
            if not reference_audio_path.exists():
                raise HTTPException(status_code=400, detail=f"Reference audio file does not exist: {job_data.reference_audio}")

        job_id = queue.enqueue(
            job_data.input_file, 
            job_data.target_lang, 
            job_data.source_lang, 
            job_data.priority,
            expressive=job_data.expressive,
            reference_audio=job_data.reference_audio
        )
        return {"job_id": job_id}

    @app.get("/api/jobs/{job_id}")
    async def get_job(job_id: str):
        job = queue.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Include checkpoint information
        checkpoint = queue.get_latest_checkpoint(job_id)
        job_dict = {
            "id": job.id,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "paused_at": job.paused_at.isoformat() if job.paused_at else None,
            "resumed_at": job.resumed_at.isoformat() if job.resumed_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "input_file": job.input_file,
            "source_lang": job.source_lang,
            "target_lang": job.target_lang,
            "output_file": job.output_file,
            "error_message": job.error_message,
            "progress_percent": job.progress_percent,
            "processing_time_seconds": job.processing_time_seconds,
            "priority": job.priority,
            "has_checkpoint": checkpoint is not None,
            "checkpoint_audio_position": checkpoint.audio_position if checkpoint else None,
            "checkpoint_created_at": checkpoint.created_at.isoformat() if checkpoint else None,
        }
        return job_dict
    
    @app.get("/api/jobs/{job_id}/checkpoints")
    async def get_job_checkpoints(job_id: str):
        """Get checkpoint history for a job."""
        job = queue.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get all checkpoints for this job
        session = queue.Session()
        checkpoints = session.query(Checkpoint).filter(
            Checkpoint.job_id == job_id
        ).order_by(Checkpoint.created_at.desc()).limit(10).all()
        
        checkpoint_list = []
        for cp in checkpoints:
            checkpoint_list.append({
                "id": cp.id,
                "created_at": cp.created_at.isoformat() if cp.created_at else None,
                "audio_position": cp.audio_position,
                "last_successful_frame": cp.last_successful_frame,
            })
        
        session.close()
        return {"checkpoints": checkpoint_list}

    @app.patch("/api/jobs/{job_id}/pause")
    async def pause_job(job_id: str):
        queue.update_job_status(job_id, JobStatus.PAUSED)
        return {"status": "paused"}

    @app.patch("/api/jobs/{job_id}/resume")
    async def resume_job(job_id: str):
        queue.update_job_status(job_id, JobStatus.QUEUED)
        return {"status": "queued"}

    @app.delete("/api/jobs/{job_id}")
    async def cancel_job(job_id: str):
        queue.update_job_status(job_id, JobStatus.FAILED, error_message="Cancelled by user")
        return {"status": "cancelled"}

    @app.get("/api/jobs/{job_id}/logs")
    async def get_job_logs(job_id: str):
        log_file = Path(cfg.paths.output_dir) / cfg.paths.logs_subdir / "app.log"
        if not log_file.exists():
            return {"logs": "No logs found."}
        
        with open(log_file, "r") as f:
            lines = f.readlines()
            return {"logs": "".join(lines[-100:])}

    @app.api_route("/api/ws/translate", methods=["GET"])
    async def websocket_endpoint(websocket: WebSocket, key: Optional[str] = None):
        client_ip = websocket.client.host if websocket.client else "unknown"
        
        # Enhanced WebSocket authentication
        if cfg.security.api_key:
            # Check query parameter first
            if key != cfg.security.api_key:
                # Also check headers (some clients send auth in headers)
                api_key_header = websocket.headers.get("X-API-KEY") or websocket.headers.get("Authorization", "").replace("Bearer ", "")
                if api_key_header != cfg.security.api_key:
                    logger.warning(f"Unauthorized WebSocket connection attempt from IP: {client_ip}")
                    await websocket.close(code=1008, reason="Policy Violation: Invalid API Key")
                    return

        await websocket.accept()
        stream_id = str(uuid.uuid4())
        logger.info(f"WebSocket connection accepted. Stream ID: {stream_id}, IP: {client_ip}")
        
        # Create a dedicated translator instance for this connection to maintain context
        stream_translator = SeamlessTranslator(cfg)
        active_streams[stream_id] = stream_translator
        
        target_lang = "deu" # Default
        source_lang = "eng" # Default
        
        try:
            # Load model for streaming
            stream_translator.load_model()
            
            while True:
                # Can receive text (json) or bytes
                message = await websocket.receive()
                
                if "text" in message:
                    import json
                    data = json.loads(message["text"])
                    if data.get("type") == "init":
                        target_lang = data.get("target_lang", "deu")
                        source_lang = data.get("source_lang", "eng")
                        logger.info(f"Stream {stream_id}: Language set to {source_lang} -> {target_lang}")
                        # Reset context when language changes
                        stream_translator.reset_streaming_context()
                        continue
                    elif data.get("type") == "reset":
                        # Allow client to reset context
                        stream_translator.reset_streaming_context()
                        await websocket.send_json({"status": "context_reset"})
                        continue
                
                if "bytes" in message:
                    data = message["bytes"]
                    try:
                        # Translate chunk with context
                        translated_bytes, translated_text = stream_translator.translate_audio_stream(
                            data, 
                            target_lang=target_lang,
                            source_lang=source_lang,
                            use_context=True  # Enable context for better translation quality
                        )
                        
                        await websocket.send_json({
                            "status": "success", 
                            "text": translated_text
                        })
                        
                    except Exception as e:
                        logger.error(f"Stream {stream_id} translation error: {e}")
                        await websocket.send_json({"error": str(e)})
                    
        except Exception as e:
            logger.info(f"WebSocket {stream_id} closed or errored: {e}")
        finally:
            # Clean up translator instance
            if stream_id in active_streams:
                del active_streams[stream_id]
            logger.info(f"WebSocket connection {stream_id} finished.")

    @app.post("/api/system/download")
    async def download_model(data: dict, background_tasks: BackgroundTasks):
        model_size = data.get("model_size", "large")
        # Update config so next time it uses this size
        cfg.model.size = model_size
        
        def run_download():
            logger.info(f"Starting background download for {model_size}...")
            m = SeamlessTranslator(cfg)
            m.load_model()
            logger.info(f"Background download for {model_size} finished.")
            
        background_tasks.add_task(run_download)
        return {"status": "download started"}

    @app.get("/api/system/config")
    async def get_config():
        return cfg.dict()

    @app.patch("/api/system/config")
    async def update_config(new_cfg: dict):
        # Update current config object
        # This is basic, for real production we'd use pydantic validation better
        for key, value in new_cfg.items():
            if hasattr(cfg, key):
                current_attr = getattr(cfg, key)
                if isinstance(current_attr, BaseModel) and isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if hasattr(current_attr, sub_key):
                            setattr(current_attr, sub_key, sub_value)
                else:
                    setattr(cfg, key, value)
        return cfg.dict()

    @app.get("/api/system/info")
    async def system_info():
        from .device_manager import get_device_info
        return get_device_info()

    @app.get("/api/system/status")
    async def system_status():
        """Get GPU memory, CPU, and queue status."""
        try:
            import psutil
        except ImportError:
            logger.warning("psutil not available, CPU/memory info will be limited")
            psutil = None
        
        import torch
        
        # Get device info
        from .device_manager import get_device_info
        device_info = get_device_info()
        
        # Get GPU memory if available
        gpu_memory = {}
        if torch.cuda.is_available():
            gpu_memory = {
                "allocated_mb": torch.cuda.memory_allocated(0) / (1024**2),
                "reserved_mb": torch.cuda.memory_reserved(0) / (1024**2),
                "total_mb": torch.cuda.get_device_properties(0).total_memory / (1024**2),
            }
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            # macOS Metal - limited memory info available
            try:
                import subprocess
                result = subprocess.run(["system_profiler", "SPDisplaysDataType"], 
                                       capture_output=True, text=True, timeout=5)
                gpu_memory = {"info": "Metal GPU detected", "available": True}
            except:
                gpu_memory = {"info": "Metal GPU", "available": True}
        
        # Get CPU info
        if psutil:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
        else:
            cpu_percent = 0.0
            cpu_count = 1
            memory = type('obj', (object,), {
                'total': 0,
                'available': 0,
                'used': 0,
                'percent': 0.0
            })()
        
        # Get queue status
        all_jobs = queue.list_jobs()
        queue_status = {
            "total": len(all_jobs),
            "queued": len([j for j in all_jobs if j.status == "queued"]),
            "running": len([j for j in all_jobs if j.status == "running"]),
            "paused": len([j for j in all_jobs if j.status == "paused"]),
            "completed": len([j for j in all_jobs if j.status == "completed"]),
            "failed": len([j for j in all_jobs if j.status == "failed"]),
        }
        
        return {
            "device": device_info,
            "gpu_memory": gpu_memory,
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
            },
            "memory": {
                "total_mb": memory.total / (1024**2),
                "available_mb": memory.available / (1024**2),
                "used_mb": memory.used / (1024**2),
                "percent": memory.percent,
            },
            "queue": queue_status,
        }

    @app.get("/api/stats")
    async def get_stats():
        """Get job completion rates and timing statistics."""
        all_jobs = queue.list_jobs()
        
        if not all_jobs:
            return {
                "total_jobs": 0,
                "completion_rate": 0.0,
                "average_processing_time": 0.0,
                "total_processing_time": 0.0,
                "by_status": {},
                "by_language": {},
            }
        
        completed_jobs = [j for j in all_jobs if j.status == "completed"]
        failed_jobs = [j for j in all_jobs if j.status == "failed"]
        
        # Calculate completion rate
        total_processed = len(completed_jobs) + len(failed_jobs)
        completion_rate = (len(completed_jobs) / total_processed * 100) if total_processed > 0 else 0.0
        
        # Calculate average processing time
        processing_times = [j.processing_time_seconds for j in completed_jobs if j.processing_time_seconds]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        total_processing_time = sum(processing_times) if processing_times else 0.0
        
        # Stats by status
        by_status = {}
        for status in ["queued", "running", "paused", "completed", "failed"]:
            by_status[status] = len([j for j in all_jobs if j.status == status])
        
        # Stats by target language
        by_language = {}
        for job in all_jobs:
            lang = job.target_lang or "unknown"
            by_language[lang] = by_language.get(lang, 0) + 1
        
        return {
            "total_jobs": len(all_jobs),
            "completion_rate": round(completion_rate, 2),
            "average_processing_time": round(avg_processing_time, 2),
            "total_processing_time": round(total_processing_time, 2),
            "completed_count": len(completed_jobs),
            "failed_count": len(failed_jobs),
            "by_status": by_status,
            "by_language": by_language,
        }

    @app.websocket("/ws/jobs/{job_id}")
    async def job_progress_websocket(websocket: WebSocket, job_id: str):
        """WebSocket endpoint for real-time job progress updates."""
        await websocket.accept()
        logger.info(f"Job progress WebSocket connected for job: {job_id}")
        
        try:
            while True:
                # Get current job status
                job = queue.get_job(job_id)
                if not job:
                    await websocket.send_json({
                        "error": "Job not found",
                        "job_id": job_id
                    })
                    break
                
                # Send current progress
                await websocket.send_json({
                    "job_id": job_id,
                    "status": job.status,
                    "progress_percent": job.progress_percent,
                    "processing_time_seconds": job.processing_time_seconds,
                })
                
                # If job is completed or failed, close connection
                if job.status in ["completed", "failed"]:
                    await websocket.send_json({
                        "job_id": job_id,
                        "status": job.status,
                        "final": True,
                    })
                    break
                
                # Wait before next update
                await asyncio.sleep(1)  # Update every second
                
        except Exception as e:
            logger.error(f"WebSocket error for job {job_id}: {e}")
        finally:
            logger.info(f"Job progress WebSocket disconnected for job: {job_id}")

    return app
