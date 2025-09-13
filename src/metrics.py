"""
Metrics computation for 3D mesh validation and analysis.
"""

import os
import trimesh
import numpy as np
from typing import Dict, Any, Optional


def compute_metrics(mesh: trimesh.Trimesh, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Compute comprehensive metrics for a 3D mesh.
    
    Args:
        mesh: Input mesh
        file_path: Optional file path for file-based metrics
    
    Returns:
        Dictionary of computed metrics
    """
    metrics = {}
    
    # Basic geometry metrics
    metrics['vertex_count'] = len(mesh.vertices)
    metrics['face_count'] = len(mesh.faces)
    metrics['edge_count'] = len(mesh.edges)
    
    # Volume and surface area
    try:
        metrics['volume'] = float(mesh.volume)
    except Exception:
        metrics['volume'] = 0.0
    
    try:
        metrics['surface_area'] = float(mesh.surface_area)
    except Exception:
        metrics['surface_area'] = 0.0
    
    # Bounding box
    bbox = mesh.bounds
    metrics['bounding_box'] = {
        'min': bbox[0].tolist(),
        'max': bbox[1].tolist(),
        'size': (bbox[1] - bbox[0]).tolist()
    }
    
    # Mesh quality metrics
    metrics['is_watertight'] = mesh.is_watertight
    metrics['is_winding_consistent'] = mesh.is_winding_consistent
    metrics['is_empty'] = mesh.is_empty
    
    # UV coordinates presence
    has_uv = hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None
    metrics['has_uv_coordinates'] = has_uv
    
    # Normals presence
    has_normals = hasattr(mesh.visual, 'vertex_normals') and mesh.visual.vertex_normals is not None
    metrics['has_vertex_normals'] = has_normals
    
    # File-based metrics
    if file_path and os.path.exists(file_path):
        file_stats = os.stat(file_path)
        metrics['file_size_bytes'] = file_stats.st_size
        metrics['file_size_mb'] = file_stats.st_size / (1024 * 1024)
    else:
        metrics['file_size_bytes'] = 0
        metrics['file_size_mb'] = 0.0
    
    # Loadability test
    metrics['loadable'] = test_mesh_loadability(mesh)
    
    # Triangle quality metrics
    if len(mesh.faces) > 0:
        face_areas = mesh.area_faces
        metrics['triangle_quality'] = {
            'min_area': float(np.min(face_areas)),
            'max_area': float(np.max(face_areas)),
            'mean_area': float(np.mean(face_areas)),
            'std_area': float(np.std(face_areas))
        }
        
        # Aspect ratio (simplified)
        try:
            aspect_ratios = []
            for face in mesh.faces:
                vertices = mesh.vertices[face]
                edges = np.linalg.norm(np.diff(vertices, axis=0), axis=1)
                if len(edges) >= 3:
                    aspect_ratio = np.max(edges) / np.min(edges)
                    aspect_ratios.append(aspect_ratio)
            
            if aspect_ratios:
                metrics['aspect_ratio'] = {
                    'min': float(np.min(aspect_ratios)),
                    'max': float(np.max(aspect_ratios)),
                    'mean': float(np.mean(aspect_ratios))
                }
        except Exception:
            metrics['aspect_ratio'] = {'min': 1.0, 'max': 1.0, 'mean': 1.0}
    
    return metrics


def test_mesh_loadability(mesh: trimesh.Trimesh) -> bool:
    """
    Test if mesh can be loaded and processed without errors.
    
    Args:
        mesh: Input mesh
    
    Returns:
        True if mesh is loadable, False otherwise
    """
    try:
        # Basic validation
        if mesh.is_empty:
            return False
        
        if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
            return False
        
        # Test basic operations
        _ = mesh.volume
        _ = mesh.surface_area
        _ = mesh.bounds
        
        # Test export/import cycle
        glb_data = mesh.export(file_type='glb')
        test_mesh = trimesh.load(io.BytesIO(glb_data), file_type='glb')
        
        return True
        
    except Exception:
        return False


def validate_mesh_quality(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate mesh quality based on computed metrics.
    
    Args:
        metrics: Computed mesh metrics
    
    Returns:
        Dictionary with validation results
    """
    validation = {
        'passed': True,
        'warnings': [],
        'errors': []
    }
    
    # Check for critical issues
    if metrics['vertex_count'] == 0:
        validation['errors'].append("Mesh has no vertices")
        validation['passed'] = False
    
    if metrics['face_count'] == 0:
        validation['errors'].append("Mesh has no faces")
        validation['passed'] = False
    
    if metrics['is_empty']:
        validation['errors'].append("Mesh is empty")
        validation['passed'] = False
    
    # Check for warnings
    if metrics['vertex_count'] > 100000:
        validation['warnings'].append("High vertex count may impact performance")
    
    if metrics['face_count'] > 50000:
        validation['warnings'].append("High face count may impact performance")
    
    if not metrics['is_watertight']:
        validation['warnings'].append("Mesh is not watertight")
    
    if not metrics['has_uv_coordinates']:
        validation['warnings'].append("Mesh lacks UV coordinates")
    
    if not metrics['loadable']:
        validation['errors'].append("Mesh failed loadability test")
        validation['passed'] = False
    
    return validation


def compare_meshes(metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare metrics between two meshes.
    
    Args:
        metrics1: First mesh metrics
        metrics2: Second mesh metrics
    
    Returns:
        Dictionary with comparison results
    """
    comparison = {
        'vertex_count_diff': metrics2['vertex_count'] - metrics1['vertex_count'],
        'face_count_diff': metrics2['face_count'] - metrics1['face_count'],
        'volume_ratio': metrics2['volume'] / metrics1['volume'] if metrics1['volume'] > 0 else 0,
        'surface_area_ratio': metrics2['surface_area'] / metrics1['surface_area'] if metrics1['surface_area'] > 0 else 0,
        'file_size_ratio': metrics2['file_size_bytes'] / metrics1['file_size_bytes'] if metrics1['file_size_bytes'] > 0 else 0
    }
    
    return comparison
