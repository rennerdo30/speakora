from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List, Optional
import asyncio
import logging
from pydantic import BaseModel
from .config import Config
from .job_queue import JobQueue, JobStatus, Job
from .translator import SeamlessTranslator

logger = logging.getLogger(__name__)

class JobCreate(BaseModel):
    input_file: str
    target_lang: str
    source_lang: str = "auto"
    priority: int = 0

def create_app(cfg: Config) -> FastAPI:
    app = FastAPI(title="S2ST Translator API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    db_path = Path(cfg.paths.output_dir) / "jobs.db"
    queue = JobQueue(db_path)
    translator = SeamlessTranslator(cfg)

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

        job_id = queue.enqueue(
            job_data.input_file, 
            job_data.target_lang, 
            job_data.source_lang, 
            job_data.priority
        )
        return {"job_id": job_id}

    @app.get("/api/jobs/{job_id}")
    async def get_job(job_id: str):
        job = queue.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

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
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        logger.info("WebSocket connection accepted.")
        
        target_lang = "deu" # Default
        
        try:
            # Load model for streaming
            translator.load_model()
            
            while True:
                # Can receive text (json) or bytes
                message = await websocket.receive()
                
                if "text" in message:
                    import json
                    data = json.loads(message["text"])
                    if data.get("type") == "init":
                        target_lang = data.get("target_lang", "deu")
                        logger.info(f"Streaming target language set to: {target_lang}")
                        continue
                
                if "bytes" in message:
                    data = message["bytes"]
                    try:
                        # Translate chunk
                        translated_bytes, translated_text = translator.translate_audio_stream(
                            data, 
                            target_lang=target_lang
                        )
                        
                        await websocket.send_json({
                            "status": "success", 
                            "text": translated_text
                        })
                        
                    except Exception as e:
                        logger.error(f"Streaming translation error: {e}")
                        await websocket.send_json({"error": str(e)})
                    
        except Exception as e:
            logger.info(f"WebSocket closed or errored: {e}")
        finally:
            logger.info("WebSocket connection finished.")

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

    return app
