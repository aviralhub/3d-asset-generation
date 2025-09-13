<xaiArtifact artifact_id="e1c79485-1e94-4efb-824d-4a45b5541d21" artifact_version_id="ec509128-997e-49b1-bd63-bf4cfaac0937" title="3D_Asset_Generation_Pipeline.md" contentType="text/markdown">

# 3D Asset Generation Pipeline - Test Scripts

This folder contains comprehensive test and validation scripts for the 3D asset generation pipeline.

---

## 🚀 Quick Start

Clone the repo and install dependencies:

```bash
git clone https://github.com/aviralhub/3d-asset-generation.git
cd 3d-asset-generation
pip install trimesh numpy
pip install pyrender matplotlib  # optional, for interactive visualization
```

Run the complete end-to-end test:

```bash
python scripts/run_test.py
```

This will:
- Generate a new asset
- Validate it
- Open an interactive 3D viewer

---

## 📂 Scripts Overview

### `run_test.py` - Main Test Harness

**Purpose:** Complete end-to-end test pipeline

**Features:**
- Generates 3D asset with detailed sci-fi crate prompt
- Validates GLB file and metadata
- Opens interactive 3D visualization
- Provides comprehensive pass/fail reporting

**Usage:**

```bash
python scripts/run_test.py
```

### `test_generation.py` - Generation Test

**Purpose:** Test asset generation with detailed prompt

**Features:**
- Uses detailed sci-fi supply crate prompt
- Tests with specific parameters (seed=42, steps=20, guidance=6.0)
- Automatically validates generated output
- Saves to `outputs/test_run/`

**Usage:**

```bash
python scripts/test_generation.py
```

### `validate_output.py` - Validation Tool

**Purpose:** Validate generated GLB files and metadata

**Features:**
- Handles both `trimesh.Trimesh` and `trimesh.Scene` objects
- Combines Scene geometries automatically
- Validates mesh properties (vertices, faces, watertightness)
- Checks metadata completeness
- Provides detailed validation results

**Usage:**

```bash
python scripts/validate_output.py
```

### `visualize_output.py` - Interactive Viewer

**Purpose:** Visualize generated 3D assets

**Features:**
- Interactive 3D viewer using `pyrender` (preferred)
- Fallback to `matplotlib` visualization
- Handles `Scene` and `Trimesh` objects
- Mouse controls for rotation, zoom, pan

**Usage:**

```bash
python scripts/visualize_output.py
```

---

## 🧪 Test Details

### Test Prompt

The test uses a highly detailed prompt designed to test the full capabilities:

```arduino
"A stylized sci-fi supply crate: rugged geometric panels, glowing cyan status panels recessed into the top and sides, reinforced riveted steel corners, small carry handle, low-poly game-ready stylization (clear silhouette), slightly worn paint chips on edges, no floating fragments, export-ready for Unity/Blender, balanced proportions."
```

### Test Parameters

- **Seed:** 42 (reproducible results)
- **Steps:** 20 (balanced complexity)
- **Guidance Scale:** 6.0 (moderate variation)
- **Output Directory:** `outputs/test_run/`

### Validation Criteria

- ✅ GLB file loads successfully
- ✅ Mesh has ≥10 vertices and faces
- ✅ Metadata contains all required fields
- ✅ Generation status is "completed"
- ✅ Files are properly structured

---

## 📊 Expected Results

For a successful test:
- **Generation:** Asset created with unique job ID
- **Vertices:** Typically 100–500 vertices
- **Faces:** Typically 200–1000 faces
- **Watertight:** Usually true for procedural generation
- **Volume:** Positive value indicating 3D content
- **File Size:** Typically 5–20 KB for GLB files

---

## 📂 Results / Outputs

All generated results are stored under `outputs/`:
- `outputs/test_run/`
  - Contains GLB files (export-ready for Unity/Blender)
  - JSON metadata files with geometry stats and validation results
  - Screenshots saved for quick preview of assets

You can open the GLB files in Blender, Unity, or any GLTF viewer.

### 📂 Outputs and Assets

- All generated files (GLB models and snapshots) are saved inside the `outputs/<run_name>/` directory.  
- Example: after a test run, you will see:


---

## 🔧 Requirements

**Required:**
- `trimesh` - 3D mesh processing
- `numpy` - Numerical operations

**Optional (for visualization):**
- `pyrender` - Interactive 3D viewer (recommended)
- `matplotlib` - Fallback visualization

**Installation:**

```bash
pip install trimesh numpy
pip install pyrender matplotlib
```

---

## ✅ Success Criteria

The pipeline is working correctly if:
- ✅ Generation completes without errors
- ✅ GLB file loads successfully in `trimesh`
- ✅ Asset has reasonable geometry (≥10 vertices/faces)
- ✅ Metadata is complete and valid
- ✅ All expected files are created
- ✅ Interactive visualization opens

---

## ⚠️ Safety Notes

- **No core changes:** These scripts only test and validate existing functionality
- **Preserves outputs:** All generated assets are saved and preserved
- **Non-destructive:** Scripts only read and validate, don't modify core code
- **Isolated testing:** Uses `outputs/test_run/` for test assets

---

## 📌 Limitations & Future Work

While the pipeline works reliably, a few limitations exist:
- Assets are currently low-poly procedural shapes without textures or UV mapping
- Style control is limited to geometric parameters, not materials or shaders
- Rigging/animation is not supported
- Visual diversity depends heavily on seed and step count

**Future Improvements:**
- Add texture & UV generation for realism
- Support rigging/animation for game-ready characters
- Integrate physics-aware validation (collisions, stability)
- Improve visual realism with advanced subdivision and shading

---

## 🎓 Conclusion

This testing suite ensures the 3D asset generation pipeline is:
- Reliable
- Validated with reproducible outputs
- Ready for academic/project submission with clear results

</xaiArtifact>