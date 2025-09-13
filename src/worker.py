"""
Simple in-memory job queue for async generation tasks.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time

from .generate import generate_asset_sync


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    prompt: str
    seed: int
    steps: int
    guidance_scale: float
    status: JobStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class JobQueue:
    """Simple in-memory job queue."""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self._running = False
    
    def submit_job(
        self,
        prompt: str,
        seed: int = 42,
        steps: int = 20,
        guidance_scale: float = 7.5
    ) -> str:
        """
        Submit a new job to the queue.
        
        Args:
            prompt: Text description for generation
            seed: Random seed for reproducibility
            steps: Number of generation steps
            guidance_scale: Guidance strength
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            prompt=prompt,
            seed=seed,
            steps=steps,
            guidance_scale=guidance_scale,
            status=JobStatus.PENDING,
            created_at=time.time()
        )
        
        self.jobs[job_id] = job
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status and results.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job status dictionary or None if not found
        """
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        status_dict = {
            "job_id": job.id,
            "status": job.status.value,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        }
        
        if job.status == JobStatus.COMPLETED and job.result:
            status_dict.update(job.result)
        elif job.status == JobStatus.FAILED and job.error:
            status_dict["error"] = job.error
        
        return status_dict
    
    async def process_job(self, job_id: str, output_dir: str = "outputs"):
        """
        Process a job asynchronously.
        
        Args:
            job_id: Job identifier
            output_dir: Output directory
        """
        job = self.jobs.get(job_id)
        if not job:
            return
        
        try:
            job.status = JobStatus.RUNNING
            job.started_at = time.time()
            
            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                generate_asset_sync,
                job.prompt,
                job.seed,
                job.steps,
                job.guidance_scale,
                output_dir
            )
            
            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = time.time()
    
    async def start_worker(self, output_dir: str = "outputs"):
        """
        Start the worker to process pending jobs.
        
        Args:
            output_dir: Output directory
        """
        self._running = True
        
        while self._running:
            # Find pending jobs
            pending_jobs = [
                job for job in self.jobs.values()
                if job.status == JobStatus.PENDING
            ]
            
            if pending_jobs:
                # Process the first pending job
                job = pending_jobs[0]
                await self.process_job(job.id, output_dir)
            else:
                # Wait a bit before checking again
                await asyncio.sleep(0.1)
    
    def stop_worker(self):
        """Stop the worker."""
        self._running = False
    
    def list_jobs(self) -> Dict[str, Dict[str, Any]]:
        """
        List all jobs and their status.
        
        Returns:
            Dictionary of job statuses
        """
        return {
            job_id: self.get_job_status(job_id)
            for job_id in self.jobs.keys()
        }


# Global job queue instance
job_queue = JobQueue()
