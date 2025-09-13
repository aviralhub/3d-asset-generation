"""
Lightweight model loader that procedurally generates 3D primitives based on prompts.
Simulates ML model behavior with parameter-based variation.
"""

import numpy as np
import trimesh
from typing import Dict, Any, Tuple
import random


class ProceduralModel:
    """Procedural 3D model generator that mimics ML model behavior."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
    
    def generate_mesh(self, prompt: str, steps: int = 20, guidance_scale: float = 7.5) -> trimesh.Trimesh:
        """
        Generate a 3D mesh based on prompt keywords and parameters.
        
        Args:
            prompt: Text description (keywords used to determine shape)
            steps: Number of generation steps (affects complexity)
            guidance_scale: Guidance strength (affects shape variation)
        
        Returns:
            Generated trimesh mesh
        """
        prompt_lower = prompt.lower()
        
        # Determine base shape from keywords
        if any(word in prompt_lower for word in ['cube', 'box', 'square']):
            base_shape = 'cube'
        elif any(word in prompt_lower for word in ['sphere', 'ball', 'round']):
            base_shape = 'sphere'
        elif any(word in prompt_lower for word in ['cylinder', 'tube', 'pipe']):
            base_shape = 'cylinder'
        elif any(word in prompt_lower for word in ['cone', 'pyramid']):
            base_shape = 'cone'
        else:
            base_shape = 'sphere'  # default
        
        # Generate base primitive
        if base_shape == 'cube':
            mesh = trimesh.creation.box(extents=[1, 1, 1])
        elif base_shape == 'sphere':
            mesh = trimesh.creation.icosphere(subdivisions=2)
        elif base_shape == 'cylinder':
            mesh = trimesh.creation.cylinder(radius=0.5, height=1.0)
        elif base_shape == 'cone':
            mesh = trimesh.creation.cone(radius=0.5, height=1.0)
        
        # Apply parameter-based modifications
        mesh = self._apply_modifications(mesh, steps, guidance_scale, prompt_lower)
        
        return mesh
    
    def _apply_modifications(self, mesh: trimesh.Trimesh, steps: int, guidance_scale: float, prompt: str) -> trimesh.Trimesh:
        """Apply modifications based on generation parameters."""
        
        # Scale based on steps (more steps = more complex)
        complexity_factor = 1.0 + (steps - 10) * 0.1
        mesh.apply_scale(complexity_factor)
        
        # Apply noise based on guidance scale
        if guidance_scale > 5.0:
            # High guidance = more variation
            noise_scale = (guidance_scale - 5.0) * 0.1
            vertices = mesh.vertices.copy()
            noise = np.random.normal(0, noise_scale, vertices.shape)
            vertices += noise
            mesh.vertices = vertices
        
        # Apply keyword-based modifications
        if 'spiky' in prompt or 'sharp' in prompt:
            # Add spikes
            mesh = self._add_spikes(mesh)
        elif 'smooth' in prompt or 'soft' in prompt:
            # Smooth the mesh
            mesh = mesh.smoothed()
        elif 'twisted' in prompt or 'spiral' in prompt:
            # Apply twist deformation
            mesh = self._apply_twist(mesh)
        
        return mesh
    
    def _add_spikes(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Add spikes to the mesh."""
        vertices = mesh.vertices.copy()
        faces = mesh.faces.copy()
        
        # Add small spikes at random vertices
        spike_indices = np.random.choice(len(vertices), size=min(10, len(vertices)//4), replace=False)
        
        for idx in spike_indices:
            vertex = vertices[idx]
            # Create a small spike
            spike_vertices = []
            spike_faces = []
            
            # Generate spike geometry
            for i in range(3):
                spike_vertex = vertex + np.random.normal(0, 0.1, 3)
                spike_vertices.append(spike_vertex)
            
            # Add spike faces (simplified)
            if len(spike_vertices) >= 3:
                spike_faces.append([len(vertices), len(vertices)+1, len(vertices)+2])
                vertices = np.vstack([vertices, spike_vertices])
                faces = np.vstack([faces, np.array(spike_faces) + len(vertices) - 3])
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)
    
    def _apply_twist(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Apply twist deformation to the mesh."""
        vertices = mesh.vertices.copy()
        
        # Apply twist around Z-axis
        center = np.mean(vertices, axis=0)
        vertices_centered = vertices - center
        
        # Calculate twist angle based on height
        z_coords = vertices_centered[:, 2]
        z_range = np.max(z_coords) - np.min(z_coords)
        if z_range > 0:
            twist_angles = (z_coords - np.min(z_coords)) / z_range * np.pi
            
            # Apply rotation
            cos_angles = np.cos(twist_angles)
            sin_angles = np.sin(twist_angles)
            
            x_new = vertices_centered[:, 0] * cos_angles - vertices_centered[:, 1] * sin_angles
            y_new = vertices_centered[:, 0] * sin_angles + vertices_centered[:, 1] * cos_angles
            
            vertices_centered[:, 0] = x_new
            vertices_centered[:, 1] = y_new
        
        vertices = vertices_centered + center
        return trimesh.Trimesh(vertices=vertices, faces=mesh.faces)


def load_model(seed: int = 42) -> ProceduralModel:
    """Load the procedural model."""
    return ProceduralModel(seed=seed)
