"""
Post-processing utilities for 3D mesh manipulation.
"""

import trimesh
import numpy as np
from typing import Optional


class PostProcessor:
    """Post-processing utilities for 3D meshes."""
    
    def __init__(self):
        pass
    
    def decimate_mesh(self, mesh: trimesh.Trimesh, target_faces: int) -> trimesh.Trimesh:
        """
        Reduce mesh complexity by decimation.
        
        Args:
            mesh: Input mesh
            target_faces: Target number of faces
        
        Returns:
            Decimated mesh
        """
        if len(mesh.faces) <= target_faces:
            return mesh
        
        try:
            # Use trimesh's built-in decimation
            decimated = mesh.simplify_quadric_decimation(face_count=target_faces)
            return decimated
        except Exception:
            # Fallback: simple face reduction
            return self._simple_decimation(mesh, target_faces)
    
    def _simple_decimation(self, mesh: trimesh.Trimesh, target_faces: int) -> trimesh.Trimesh:
        """Simple decimation by removing faces."""
        if len(mesh.faces) <= target_faces:
            return mesh
        
        # Randomly select faces to keep
        keep_indices = np.random.choice(
            len(mesh.faces), 
            size=target_faces, 
            replace=False
        )
        
        new_faces = mesh.faces[keep_indices]
        
        # Rebuild mesh with new faces
        return trimesh.Trimesh(vertices=mesh.vertices, faces=new_faces)
    
    def generate_lod(self, mesh: trimesh.Trimesh, lod_level: int) -> trimesh.Trimesh:
        """
        Generate a Level of Detail (LOD) version of the mesh.
        
        Args:
            mesh: Input mesh
            lod_level: LOD level (0=highest detail, higher=lower detail)
        
        Returns:
            LOD mesh
        """
        reduction_factor = 1.0 / (2 ** lod_level)
        target_faces = max(10, int(len(mesh.faces) * reduction_factor))
        
        return self.decimate_mesh(mesh, target_faces)
    
    def convert_format(self, mesh: trimesh.Trimesh, format: str) -> bytes:
        """
        Convert mesh to different format.
        
        Args:
            mesh: Input mesh
            format: Target format ('glb', 'obj', 'ply')
        
        Returns:
            Mesh data in target format
        """
        if format.lower() == 'glb':
            return mesh.export(file_type='glb')
        elif format.lower() == 'obj':
            return mesh.export(file_type='obj')
        elif format.lower() == 'ply':
            return mesh.export(file_type='ply')
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def optimize_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """
        Optimize mesh for better performance.
        
        Args:
            mesh: Input mesh
        
        Returns:
            Optimized mesh
        """
        # Remove duplicate vertices
        mesh.remove_duplicate_vertices()
        
        # Remove unused vertices
        mesh.remove_unused_vertices()
        
        # Merge vertices that are very close
        mesh.merge_vertices(merge_tex=True, merge_norm=True)
        
        return mesh
    
    def add_uv_coordinates(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """
        Add UV coordinates to mesh if missing.
        
        Args:
            mesh: Input mesh
        
        Returns:
            Mesh with UV coordinates
        """
        if hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None:
            return mesh
        
        # Generate simple UV coordinates
        vertices = mesh.vertices
        
        # Simple planar projection
        u = (vertices[:, 0] - vertices[:, 0].min()) / (vertices[:, 0].max() - vertices[:, 0].min())
        v = (vertices[:, 1] - vertices[:, 1].min()) / (vertices[:, 1].max() - vertices[:, 1].min())
        
        uv = np.column_stack([u, v])
        
        # Create new mesh with UV coordinates
        new_mesh = mesh.copy()
        new_mesh.visual.uv = uv
        
        return new_mesh
