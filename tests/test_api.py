"""
Tests for the FastAPI application.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import json
import os
import tempfile
import shutil

from src.api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_generate_sync(client, temp_output_dir):
    """Test synchronous generation endpoint."""
    # Override output directory for test
    os.environ["TEST_OUTPUT_DIR"] = temp_output_dir
    
    request_data = {
        "prompt": "test cube",
        "seed": 42,
        "steps": 10,
        "guidance_scale": 5.0,
        "sync": True
    }
    
    response = client.post("/generate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "completed"
    assert "message" in data


def test_generate_async(client):
    """Test asynchronous generation endpoint."""
    request_data = {
        "prompt": "test sphere",
        "seed": 123,
        "steps": 15,
        "guidance_scale": 7.0,
        "sync": False
    }
    
    response = client.post("/generate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert "message" in data
    
    # Check job status
    job_id = data["job_id"]
    status_response = client.get(f"/status/{job_id}")
    assert status_response.status_code == 200
    
    status_data = status_response.json()
    assert status_data["job_id"] == job_id
    assert "status" in status_data


def test_job_status_not_found(client):
    """Test job status endpoint with non-existent job."""
    response = client.get("/status/non-existent-job-id")
    assert response.status_code == 404


def test_list_jobs(client):
    """Test list jobs endpoint."""
    response = client.get("/jobs")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)


def test_test_endpoint(client):
    """Test the test endpoint."""
    response = client.get("/test")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "message" in data


def test_generate_with_minimal_params(client):
    """Test generation with minimal parameters."""
    request_data = {
        "prompt": "simple box"
    }
    
    response = client.post("/generate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


def test_generate_invalid_request(client):
    """Test generation with invalid request."""
    request_data = {
        "invalid_field": "test"
    }
    
    response = client.post("/generate", json=request_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_async_generation_flow(client):
    """Test complete async generation flow."""
    # Submit job
    request_data = {
        "prompt": "async test cube",
        "seed": 456,
        "steps": 12,
        "guidance_scale": 6.0,
        "sync": False
    }
    
    response = client.post("/generate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    job_id = data["job_id"]
    
    # Wait a bit for processing (in real scenario, this would be handled by worker)
    await asyncio.sleep(0.1)
    
    # Check status
    status_response = client.get(f"/status/{job_id}")
    assert status_response.status_code == 200
    
    status_data = status_response.json()
    assert status_data["job_id"] == job_id
    assert status_data["status"] in ["pending", "running", "completed", "failed"]


def test_multiple_generations(client):
    """Test multiple simultaneous generations."""
    requests = [
        {"prompt": f"cube {i}", "sync": True}
        for i in range(3)
    ]
    
    responses = []
    for request_data in requests:
        response = client.post("/generate", json=request_data)
        assert response.status_code == 200
        responses.append(response.json())
    
    # All should have completed
    for data in responses:
        assert data["status"] == "completed"
        assert "job_id" in data
