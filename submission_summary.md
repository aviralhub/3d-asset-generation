# Submission Summary

This document summarizes the pipeline, methodology, and findings of our 3D asset generation assignment.

---

## 🛠 Toolchain & Methodology

- **Core Libraries:**  
  - `trimesh` for procedural geometry construction and mesh validation.  
  - `numpy` for randomization and parameter control.  
  - Custom scripts in `src/` for generation, saving, and validation.  

- **Output Format:**  
  - Assets are stored as `.glb` files in `outputs/` directory.  
  - Screenshots are generated alongside GLB files for quick inspection.  

- **Validation Metrics:**  
  - Mesh watertightness check.  
  - Face/vertex counts.  
  - File size reporting.  

This ensures generated assets are not only **visually valid** but also **structurally correct** for downstream use.

---

## 💡 Why This Approach?

- **CPU-friendly:** Designed to run on modest hardware without GPU acceleration.  
- **Reproducible:** Random seeds guarantee deterministic asset generation.  
- **Extendable:** Modular codebase allows future additions (e.g., textures, rigging, UV mapping).  

This makes the pipeline suitable for academic, experimental, and lightweight game prototyping scenarios.

---

## 🔬 Experiments Conducted

1. **Random Seed Variation**  
   - Prompt kept constant, different seeds tested.  
   - Result: Diversity in structure while preserving prompt fidelity.  
   - Reproducible → same seed gives identical mesh.  

2. **Steps / Subdivision Variation**  
   - Tested 10, 20, and 40 steps.  
   - Result:  
     - 10 → blocky, rough.  
     - 20 → balanced, smooth, game-ready.  
     - 40 → highly detailed but heavy.  

**Screenshots and detailed results** are in [`experiments.md`](./experiments.md).

---

## 📈 Observations

- Seeds effectively provide **creative diversity**.  
- Steps act as a **quality–efficiency trade-off knob**.  
- Generated assets are small in size (<0.05 MB), watertight, and compatible with 3D tools.  

---

## 🚀 Limitations & Future Work

- **Textures & Materials:** Currently meshes are untextured, limiting realism.  
- **UV Mapping:** Automatic UVs not yet supported.  
- **Rigging/Animation:** Only static meshes supported.  
- **Prompt Sensitivity:** Complex descriptive prompts often collapse to simple geometry.  

**Future improvements** could integrate:  
- Diffusion-based mesh detail generation.  
- Procedural texturing and material assignment.  
- Basic rigging for animated assets.  
- Better prompt-to-shape fidelity through learned models.

---

## ✅ Final Notes

The pipeline demonstrates a **working, reproducible baseline** for procedural 3D asset generation.  
It balances **simplicity, correctness, and efficiency**, making it a strong foundation for future extensions in realism and usability.
