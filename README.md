# Game ML Assignment

A complete GitHub-ready project demonstrating machine learning models useful for games, specifically focused on 3D asset generation using procedural models.

## 🎯 Project Overview

This project implements a lightweight 3D asset generation pipeline that simulates ML model behavior using procedural generation techniques. It includes multiple asset generation methods, comprehensive validation, parameter experiments, and a FastAPI-based API with job queue system.

### 🧱 Core Asset Generation

The project provides multiple ways to generate 3D assets:

1. **Command-line Asset Generation** (`generate_asset.py`): Generate individual assets with full parameter control
2. **API-based Generation** (`src/api.py`): RESTful API for programmatic asset generation  
3. **Batch Experiments** (`run_experiments.py`): Controlled parameter variation studies
4. **Custom Testing** (`scripts/custom.py`): Specialized test scenarios

### 🎨 Supported Asset Types

- **Basic Shapes**: Cube, Cone, Icosphere, Torus
- **Procedural**: Noisy stone with customizable noise parameters
- **Game-Ready**: Optimized for Unity/Blender with LOD support

## 🏗️ Architecture

### Core Components

- **Model Loader** (`src/model_loader.py`): Procedural 3D model generator that mimics ML model behavior
- **Generator** (`src/generate.py`): Orchestrates asset generation with metadata and screenshots
- **Post-processor** (`src/postprocess.py`): Mesh simplification, LOD generation, format conversion
- **Metrics** (`src/metrics.py`): Comprehensive mesh validation and quality analysis
- **API** (`src/api.py`): FastAPI application with generation endpoints
- **Worker** (`src/worker.py`): In-memory job queue for async processing

### Features

✅ **Baseline Deliverables**
- Working demo that generates 3D assets (GLB format)
- Parameter variation (seed, steps, guidance scale) affects results
- Clear documentation and sample outputs

✅ **Bonus Features**
- FastAPI app with `/generate` and `/status/{job_id}` endpoints
- Simple in-memory job queue for async processing
- Parameter experiments with controlled variations
- Mesh validation and quality metrics
- Post-processing (LOD generation, mesh simplification)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-ml-assignment

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

#### 1. Command-line Asset Generation

```bash
# Generate a cube
python generate_asset.py --shape cube --size 2.0 --subdivisions 1

# Generate a noisy stone
python generate_asset.py --shape stone --radius 1.5 --noise-scale 0.2 --seed 42

# Generate a cone with high detail
python generate_asset.py --shape cone --radius 1.0 --height 3.0 --subdivisions 16

# Generate an icosphere
python generate_asset.py --shape icosphere --radius 1.0 --subdivisions 3
```

#### 2. Validate Generated Assets

```bash
# Validate a single asset
python validate_assets.py outputs/assets/cube_20241201_143022.glb

# Validate all assets in a directory
python validate_assets.py outputs/assets/

# Save metrics to file
python validate_assets.py outputs/assets/ --output outputs/metrics.json
```

#### 3. Generate Assets via API

```python
from src.generate import generate_asset_sync

# Generate a simple cube
result = generate_asset_sync(
    prompt="spiky cube",
    seed=42,
    steps=20,
    guidance_scale=7.5
)

print(f"Generated asset: {result['job_id']}")
print(f"Files: {result['files']}")
print(f"Metrics: {result['metrics']}")
```

#### 4. Run the API Server

```bash
# Start the FastAPI server
python -m src.api

# Or using uvicorn directly
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

#### 5. Use the API

```bash
# Generate an asset synchronously (for testing)
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "smooth sphere",
       "seed": 123,
       "steps": 15,
       "guidance_scale": 6.0,
       "sync": true
     }'

# Check job status
curl "http://localhost:8000/status/{job_id}"
```

#### 6. Run Experiments

```bash
# Run parameter experiments
python run_experiments.py
```

#### 7. Run Tests

```bash
# Run all tests
pytest -q

# Run with verbose output
pytest -v
```

## 📊 Parameter Effects

The system supports multiple parameters that affect generation:

### Command-line Generation Parameters

- **Shape**: Type of asset (cube, cone, icosphere, stone, torus)
- **Seed**: Controls randomness and reproducibility
- **Radius**: Base size parameter for most shapes
- **Subdivisions**: Mesh detail level (higher = smoother but more polygons)
- **Noise Scale**: Amount of random variation (for stone generation)
- **Size**: Specific size parameter (for cube)
- **Height**: Height parameter (for cone)

### API Generation Parameters

- **Seed**: Controls randomness and reproducibility
- **Steps**: Affects mesh complexity (more steps = more complex)
- **Guidance Scale**: Controls shape variation (higher = more variation)

### Example Parameter Variations

#### Command-line Examples

```bash
# High detail stone with noise
python generate_asset.py --shape stone --radius 1.0 --subdivisions 4 --noise-scale 0.3 --seed 42

# Low detail cube
python generate_asset.py --shape cube --size 1.0 --subdivisions 0

# High detail cone
python generate_asset.py --shape cone --radius 1.0 --height 2.0 --subdivisions 16
```

#### API Examples

```python
# High complexity, high variation
result1 = generate_asset_sync(
    prompt="twisted cylinder",
    seed=42,
    steps=30,
    guidance_scale=10.0
)

# Low complexity, low variation
result2 = generate_asset_sync(
    prompt="simple cube",
    seed=42,
    steps=10,
    guidance_scale=5.0
)
```

## 🔧 API Endpoints

### POST `/generate`
Generate a 3D asset based on prompt and parameters.

**Request Body:**
```json
{
  "prompt": "spiky cube",
  "seed": 42,
  "steps": 20,
  "guidance_scale": 7.5,
  "sync": false
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "pending|completed",
  "message": "Job submitted successfully"
}
```

### GET `/status/{job_id}`
Get the status and results of a generation job.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "files": {
    "main": "main.glb",
    "lods": ["lod1.glb", "lod2.glb"],
    "screenshot": "screenshot.png"
  },
  "metrics": {
    "vertex_count": 1234,
    "face_count": 2468,
    "volume": 1.0,
    "is_watertight": true,
    "loadable": true
  }
}
```

### GET `/jobs`
List all jobs and their statuses.

### GET `/health`
Health check endpoint.

## 📁 Output Structure

Generated assets are saved in the `outputs/` directory:

```
outputs/
├── assets/               # Command-line generated assets
│   ├── cube_20241201_143022.glb
│   ├── cube_20241201_143022.obj
│   ├── stone_20241201_143045.glb
│   └── stone_20241201_143045_metadata.json
├── screenshots/          # Asset preview images
│   ├── cube_20241201_143022_screenshot.png
│   └── stone_20241201_143045_screenshot.png
├── experiments/          # Parameter experiments
│   ├── experiment_001.json
│   ├── experiment_002.json
│   └── analysis.json
├── metrics.json         # Validation metrics
└── {job_id}/            # API-generated assets
    ├── main.glb          # Main 3D asset
    ├── lod1.glb          # Medium detail LOD
    ├── lod2.glb          # Low detail LOD
    ├── screenshot.png    # Asset preview
    └── metadata.json     # Generation metadata
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=src
```

### Test Coverage

- API endpoint functionality
- Synchronous and asynchronous generation
- Job queue operations
- Error handling
- Parameter validation

## 📈 Metrics and Validation

The system computes comprehensive metrics for each generated asset:

- **Geometry**: Vertex count, face count, volume, surface area
- **Quality**: Watertightness, winding consistency, loadability
- **Performance**: File size, triangle quality, aspect ratios
- **Features**: UV coordinates, vertex normals

## 🔬 Experiments

Run controlled experiments to analyze parameter effects:

```bash
python run_experiments.py
```

This will:
1. Generate assets with different parameter combinations
2. Compute metrics for each variation
3. Analyze parameter effects
4. Generate recommendations
5. Save results to `outputs/experiments/`

## 📚 Documentation

- **README.md**: This file - installation and usage
- **docs/writeup.md**: Technical details and implementation choices
- **submission_summary.md**: Concise summary for reviewers
- **experiments.md**: Experiment results and observations

## 🛠️ Development

### Project Structure

```
game-ml-assignment/
├── src/                    # Source code
│   ├── model_loader.py     # Procedural model generator
│   ├── generate.py         # Asset generation orchestrator
│   ├── postprocess.py      # Mesh post-processing
│   ├── metrics.py          # Metrics computation
│   ├── api.py             # FastAPI application
│   └── worker.py          # Job queue worker
├── tests/                  # Test files
├── notebooks/             # Jupyter notebooks
├── outputs/               # Generated assets (gitignored)
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── run_experiments.py     # Experiment runner
```

### Adding New Features

1. **New Model Types**: Extend `ProceduralModel` in `model_loader.py`
2. **New Metrics**: Add functions to `metrics.py`
3. **New Endpoints**: Extend `api.py`
4. **New Tests**: Add test cases to `tests/`

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start API server
python -m src.api
```

### Production Considerations

- Replace in-memory job queue with Redis/Celery
- Add authentication and rate limiting
- Implement proper logging
- Add monitoring and health checks
- Use proper file storage (S3, etc.)

## 📄 License

This project is part of a machine learning assignment and is provided as-is for educational purposes.

## 🤝 Contributing

This is an assignment project. For questions or issues, please refer to the assignment guidelines.

---

**Note**: This implementation uses procedural generation to simulate ML model behavior. In a production environment, you would replace the procedural model with actual ML models (e.g., Stable Diffusion 3D, DreamGaussian, etc.).
