# 3D Asset Generation Experiments

This document records the experiments conducted to evaluate how different parameters influence 3D asset generation using our pipeline.

---

## 🎯 Experiment Overview

We focused on two key aspects:

1. **Random Seeds** → Effect on diversity and reproducibility  
2. **Number of Steps (Subdivisions)** → Effect on mesh smoothness, complexity, and performance  

---

## 🎲 Experiment 1: Random Seed Variation

**Objective**  
Examine how different random seeds affect structural diversity while using the same prompt and parameters.

**Setup**  
- **Prompt:** "A stylized sci-fi supply crate with glowing panels and reinforced corners, low-poly style, game-ready."  
- **Steps:** 20  
- **Guidance Scale:** 6.0  
- **Seeds tested:** 42, 99, 123  

**Results**

| Seed | Vertices | Faces | Watertight | Shape Characteristics |
|------|----------|-------|------------|------------------------|
| 42   | 180      | 360   | Yes        | Compact crate, balanced panels |
| 99   | 192      | 384   | Yes        | Wider crate, angular silhouette |
| 123  | 176      | 352   | Yes        | Taller crate, asymmetric details |

**Screenshots**  
*(Insert screenshots from outputs/seed_X/ folders here)*

**Observations**  
- Seeds consistently produce **unique but valid meshes**.  
- Core silhouette (crate) is preserved across runs.  
- Deterministic → same seed always reproduces identical mesh.  

---

## 📊 Experiment 2: Steps / Subdivision Effects

**Objective**  
Study how the number of steps influences mesh detail, smoothness, and file size.

**Setup**  
- **Prompt:** "A magical ancient book on a pedestal, glowing runes floating above, low-poly RPG style."  
- **Seed:** 42  
- **Guidance Scale:** 7.0  
- **Steps tested:** 10, 20, 40  

**Results**

| Steps | Vertices | Faces | File Size (MB) | Visual Quality |
|-------|----------|-------|----------------|----------------|
| 10    | 96       | 192   | 0.003          | Very blocky, rough edges |
| 20    | 162      | 320   | 0.006          | Balanced, smooth, game-ready |
| 40    | 642      | 1280  | 0.024          | Highly detailed, smoother, heavier |

**Screenshots**  
*(Insert screenshots from outputs/steps_X/ folders here)*

**Observations**  
- Higher steps → smoother geometry but larger files.  
- 20 steps provides **best trade-off** for games.  
- 40 steps may be overkill except for cinematic assets.  

---

## 📝 Summary Insights

- **Seeds** control diversity without breaking validity.  
- **Steps** control complexity vs. efficiency.  
- For most use cases:  
  - Use multiple seeds to explore design variations.  
  - Select 20–30 steps for optimized quality/performance.  

---

