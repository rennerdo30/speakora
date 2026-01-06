from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Optional, Any
import json
from sqlalchemy import (
    create_engine, Column, String, Float, DateTime, Integer, Text, ForeignKey, PickleType
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import uuid

Base = declarative_base()

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    status = Column(String, default=JobStatus.QUEUED)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    resumed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    input_file = Column(Text, nullable=False)
    source_lang = Column(String, nullable=True)
    target_lang = Column(String, nullable=False)
    output_file = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    progress_percent = Column(Float, default=0.0)
    processing_time_seconds = Column(Float, nullable=True)
    priority = Column(Integer, default=0)

    checkpoints = relationship("Checkpoint", back_populates="job", cascade="all, delete-orphan")

class Checkpoint(Base):
    __tablename__ = "checkpoints"
    
    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    checkpoint_data = Column(PickleType)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    audio_position = Column(Integer, default=0)
    last_successful_frame = Column(Integer, nullable=True)
    checksum = Column(String, nullable=True)

    job = relationship("Job", back_populates="checkpoints")

class JobQueue:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def enqueue(self, input_file: str, target_lang: str, source_lang: Optional[str] = "auto", priority: int = 0) -> str:
        session = self.Session()
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            input_file=input_file,
            target_lang=target_lang,
            source_lang=source_lang,
            priority=priority
        )
        session.add(job)
        session.commit()
        session.close()
        return job_id

    def list_jobs(self, status: Optional[str] = None) -> List[Job]:
        session = self.Session()
        query = session.query(Job)
        if status:
            query = query.filter(Job.status == status)
        jobs = query.order_by(Job.priority.desc(), Job.created_at.asc()).all()
        # Detach from session to avoid issues when closing session
        session.expunge_all()
        session.close()
        return jobs

    def get_job(self, job_id: str) -> Optional[Job]:
        session = self.Session()
        job = session.query(Job).filter(Job.id == job_id).first()
        if job:
            session.expunge(job)
        session.close()
        return job

    def update_job_status(self, job_id: str, status: JobStatus, **kwargs):
        session = self.Session()
        job = session.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            if status == JobStatus.RUNNING:
                if not job.started_at:
                    job.started_at = datetime.now(timezone.utc)
                else:
                    job.resumed_at = datetime.now(timezone.utc)
            elif status == JobStatus.PAUSED:
                job.paused_at = datetime.now(timezone.utc)
            elif status == JobStatus.COMPLETED:
                job.completed_at = datetime.now(timezone.utc)
            
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            session.commit()
        session.close()


    def save_checkpoint(self, job_id: str, data: Any, audio_position: int = 0):
        session = self.Session()
        checkpoint_id = str(uuid.uuid4())
        checkpoint = Checkpoint(
            id=checkpoint_id,
            job_id=job_id,
            checkpoint_data=data,
            audio_position=audio_position
        )
        session.add(checkpoint)
        session.commit()
        session.close()

    def get_latest_checkpoint(self, job_id: str) -> Optional[Checkpoint]:
        session = self.Session()
        checkpoint = session.query(Checkpoint).filter(Checkpoint.job_id == job_id).order_by(Checkpoint.created_at.desc()).first()
        if checkpoint:
            session.expunge(checkpoint)
        session.close()
        return checkpoint
