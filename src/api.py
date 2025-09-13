"""
FastAPI application with endpoints for 3D asset generation.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import threading

from .worker import job_queue, JobStatus
from .generate import generate_asset_sync


app = FastAPI(
    title="Game ML Assignment API",
    description="API for generating 3D assets using procedural models",
    version="1.0.0"
)


class GenerationRequest(BaseModel):
    prompt: str
    seed: Optional[int] = 42
    steps: Optional[int] = 20
    guidance_scale: Optional[float] = 7.5
    sync: Optional[bool] = False


class GenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str


@app.on_event("startup")
async def startup_event():
    """Start the background worker on startup."""
    # Start worker in background thread
    def run_worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(job_queue.start_worker())
    
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Game ML Assignment API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/generate",
            "status": "/status/{job_id}",
            "jobs": "/jobs"
        }
    }


@app.post("/generate", response_model=GenerationResponse)
async def generate_asset(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate a 3D asset based on the provided prompt and parameters.
    
    Args:
        request: Generation request with prompt and parameters
        background_tasks: FastAPI background tasks
    
    Returns:
        Generation response with job ID and status
    """
    try:
        if request.sync:
            # Synchronous generation for testing
            result = generate_asset_sync(
                prompt=request.prompt,
                seed=request.seed,
                steps=request.steps,
                guidance_scale=request.guidance_scale
            )
            
            return GenerationResponse(
                job_id=result["job_id"],
                status="completed",
                message="Asset generated successfully"
            )
        else:
            # Asynchronous generation
            job_id = job_queue.submit_job(
                prompt=request.prompt,
                seed=request.seed,
                steps=request.steps,
                guidance_scale=request.guidance_scale
            )
            
            return GenerationResponse(
                job_id=job_id,
                status="pending",
                message="Job submitted successfully"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a generation job.
    
    Args:
        job_id: Job identifier
    
    Returns:
        Job status and results
    """
    status = job_queue.get_job_status(job_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status


@app.get("/jobs")
async def list_jobs():
    """
    List all jobs and their statuses.
    
    Returns:
        Dictionary of all jobs
    """
    return job_queue.list_jobs()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


# Test endpoint for quick validation
@app.get("/test")
async def test_endpoint():
    """Test endpoint that generates a simple asset synchronously."""
    try:
        result = generate_asset_sync(
            prompt="test cube",
            seed=42,
            steps=10,
            guidance_scale=5.0
        )
        
        return {
            "status": "success",
            "message": "Test generation completed",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Test generation failed: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
