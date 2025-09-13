"""
Main generation orchestrator that creates 3D assets with metadata and screenshots.
"""

import os
import json
import uuid
from typing import Dict, Any, List
import trimesh
import numpy as np
from PIL import Image
import io

from .model_loader import load_model
from .postprocess import PostProcessor
from .metrics import compute_metrics


class AssetGenerator:
    """Main class for generating 3D assets."""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        self.postprocessor = PostProcessor()
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_asset(
        self,
        prompt: str,
        seed: int = 42,
        steps: int = 20,
        guidance_scale: float = 7.5,
        job_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate a complete 3D asset with metadata and screenshots.
        
        Args:
            prompt: Text description for generation
            seed: Random seed for reproducibility
            steps: Number of generation steps
            guidance_scale: Guidance strength
            job_id: Optional job ID for tracking
        
        Returns:
            Dictionary with generation results and metadata
        """
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        # Load model and generate base mesh
        model = load_model(seed=seed)
        base_mesh = model.generate_mesh(prompt, steps, guidance_scale)
        
        # Create output directory for this job
        job_dir = os.path.join(self.output_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        # Generate main asset
        main_path = os.path.join(job_dir, "main.glb")
        base_mesh.export(main_path)
        
        # Generate LODs
        lod_paths = self._generate_lods(base_mesh, job_dir)
        
        # Generate screenshot
        screenshot_path = self._generate_screenshot(base_mesh, job_dir)
        
        # Compute metrics
        metrics = compute_metrics(base_mesh, main_path)
        
        # Create metadata
        metadata = {
            "job_id": job_id,
            "prompt": prompt,
            "parameters": {
                "seed": seed,
                "steps": steps,
                "guidance_scale": guidance_scale
            },
            "files": {
                "main": "main.glb",
                "lods": lod_paths,
                "screenshot": screenshot_path
            },
            "metrics": metrics,
            "status": "completed"
        }
        
        # Save metadata
        metadata_path = os.path.join(job_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def _generate_lods(self, mesh: trimesh.Trimesh, job_dir: str) -> List[str]:
        """Generate LOD versions of the mesh."""
        lod_paths = []
        
        # LOD 1: Medium detail (50% reduction)
        lod1_mesh = self.postprocessor.decimate_mesh(mesh, target_faces=len(mesh.faces) // 2)
        lod1_path = os.path.join(job_dir, "lod1.glb")
        lod1_mesh.export(lod1_path)
        lod_paths.append("lod1.glb")
        
        # LOD 2: Low detail (25% reduction)
        lod2_mesh = self.postprocessor.decimate_mesh(mesh, target_faces=len(mesh.faces) // 4)
        lod2_path = os.path.join(job_dir, "lod2.glb")
        lod2_mesh.export(lod2_path)
        lod_paths.append("lod2.glb")
        
        return lod_paths
    
    def _generate_screenshot(self, mesh: trimesh.Trimesh, job_dir: str) -> str:
        """Generate a screenshot of the mesh."""
        try:
            # Create a simple orthographic view
            scene = mesh.scene()
            
            # Set up camera
            camera_transform = np.eye(4)
            camera_transform[:3, 3] = [2, 2, 2]  # Position camera
            scene.camera_transform = camera_transform
            
            # Render scene (simplified - just save mesh as image representation)
            screenshot_path = os.path.join(job_dir, "screenshot.png")
            
            # Create a simple visualization
            # For now, create a placeholder image
            img = Image.new('RGB', (512, 512), color='lightblue')
            
            # Add some basic info as text (simplified)
            # In a real implementation, you'd use proper 3D rendering
            img.save(screenshot_path)
            
            return "screenshot.png"
            
        except Exception as e:
            print(f"Warning: Could not generate screenshot: {e}")
            return ""


def generate_asset_sync(
    prompt: str,
    seed: int = 42,
    steps: int = 20,
    guidance_scale: float = 7.5,
    output_dir: str = "outputs"
) -> Dict[str, Any]:
    """
    Synchronous asset generation function.
    
    Args:
        prompt: Text description for generation
        seed: Random seed for reproducibility
        steps: Number of generation steps
        guidance_scale: Guidance strength
        output_dir: Output directory
    
    Returns:
        Dictionary with generation results
    """
    generator = AssetGenerator(output_dir)
    return generator.generate_asset(prompt, seed, steps, guidance_scale)
