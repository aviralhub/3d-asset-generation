#!/usr/bin/env python3
"""
Asset Validation Script for 3D Game Assets
Validates GLB/OBJ files and reports comprehensive metrics.
"""

import argparse
import json
import os
from pathlib import Path
import trimesh
import numpy as np
from datetime import datetime

def validate_mesh(mesh_path):
    """Validate a single mesh file and return comprehensive metrics."""
    print(f"🔍 Validating: {mesh_path}")
    
    try:
        # Load mesh
        mesh = trimesh.load(str(mesh_path))
        
        # Handle Scene objects (combine geometries)
        if isinstance(mesh, trimesh.Scene):
            print("⚠️  Scene detected, combining geometries...")
            if len(mesh.geometry) == 0:
                raise ValueError("Scene has no geometry")
            geometries = list(mesh.geometry.values())
            mesh = trimesh.util.concatenate(geometries)
            print(f"   Combined {len(geometries)} geometries")
        
        # Basic mesh properties
        metrics = {
            'file_path': str(mesh_path),
            'file_size_bytes': mesh_path.stat().st_size,
            'file_size_mb': mesh_path.stat().st_size / (1024 * 1024),
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces),
            'edges': len(mesh.edges),
            'is_watertight': mesh.is_watertight,
            'is_empty': mesh.is_empty,
            'is_winding_consistent': mesh.is_winding_consistent,
            'volume': float(mesh.volume) if hasattr(mesh, 'volume') else 0.0,
            'surface_area': float(mesh.surface_area) if hasattr(mesh, 'surface_area') else 0.0,
        }
        
        # Bounding box
        metrics['bounding_box'] = {
            'min': mesh.bounds[0].tolist(),
            'max': mesh.bounds[1].tolist(),
            'size': (mesh.bounds[1] - mesh.bounds[0]).tolist(),
            'center': mesh.centroid.tolist()
        }
        
        # Normals
        metrics['normals'] = {
            'has_vertex_normals': hasattr(mesh, 'vertex_normals') and mesh.vertex_normals is not None,
            'has_face_normals': hasattr(mesh, 'face_normals') and mesh.face_normals is not None,
            'vertex_normal_count': len(mesh.vertex_normals) if hasattr(mesh, 'vertex_normals') and mesh.vertex_normals is not None else 0,
            'face_normal_count': len(mesh.face_normals) if hasattr(mesh, 'face_normals') and mesh.face_normals is not None else 0
        }
        
        # UV coordinates
        metrics['uv_coordinates'] = {
            'has_uv': hasattr(mesh, 'visual') and hasattr(mesh.visual, 'uv'),
            'uv_count': len(mesh.visual.uv) if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'uv') else 0
        }
        
        # Triangle quality metrics
        if len(mesh.faces) > 0:
            face_areas = mesh.area_faces
            metrics['triangle_quality'] = {
                'min_area': float(np.min(face_areas)),
                'max_area': float(np.max(face_areas)),
                'mean_area': float(np.mean(face_areas)),
                'std_area': float(np.std(face_areas)),
                'total_area': float(np.sum(face_areas))
            }
        
        # Edge length metrics
        if len(mesh.edges) > 0:
            edge_lengths = mesh.edges_unique_length
            metrics['edge_quality'] = {
                'min_length': float(np.min(edge_lengths)),
                'max_length': float(np.max(edge_lengths)),
                'mean_length': float(np.mean(edge_lengths)),
                'std_length': float(np.std(edge_lengths))
            }
        
        # Validation checks
        validation_checks = {
            'has_minimum_geometry': metrics['vertices'] >= 3 and metrics['faces'] >= 1,
            'is_manifold': mesh.is_watertight,
            'has_normals': metrics['normals']['has_vertex_normals'] or metrics['normals']['has_face_normals'],
            'reasonable_polycount': metrics['faces'] <= 100000,  # Reasonable limit for games
            'positive_volume': metrics['volume'] > 0,
            'file_size_reasonable': metrics['file_size_mb'] <= 50  # 50MB limit
        }
        
        metrics['validation_checks'] = validation_checks
        metrics['validation_passed'] = all(validation_checks.values())
        
        print(f"✅ Validation successful")
        return metrics
        
    except Exception as e:
        error_metrics = {
            'file_path': str(mesh_path),
            'error': str(e),
            'validation_passed': False,
            'file_size_bytes': mesh_path.stat().st_size if mesh_path.exists() else 0,
            'file_size_mb': mesh_path.stat().st_size / (1024 * 1024) if mesh_path.exists() else 0
        }
        print(f"❌ Validation failed: {e}")
        return error_metrics

def validate_directory(directory_path):
    """Validate all mesh files in a directory."""
    directory = Path(directory_path)
    if not directory.exists():
        print(f"❌ Directory not found: {directory_path}")
        return []
    
    # Find all mesh files
    mesh_extensions = ['.glb', '.obj', '.ply', '.stl']
    mesh_files = []
    
    for ext in mesh_extensions:
        mesh_files.extend(directory.glob(f"*{ext}"))
    
    if not mesh_files:
        print(f"⚠️  No mesh files found in {directory_path}")
        return []
    
    print(f"📁 Found {len(mesh_files)} mesh files to validate")
    
    all_metrics = []
    for mesh_file in mesh_files:
        metrics = validate_mesh(mesh_file)
        all_metrics.append(metrics)
        print()  # Add spacing between files
    
    return all_metrics

def print_summary(metrics_list):
    """Print a summary of validation results."""
    if not metrics_list:
        print("📊 No metrics to summarize")
        return
    
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    total_files = len(metrics_list)
    passed_files = sum(1 for m in metrics_list if m.get('validation_passed', False))
    failed_files = total_files - passed_files
    
    print(f"Total files: {total_files}")
    print(f"Passed: {passed_files}")
    print(f"Failed: {failed_files}")
    print(f"Success rate: {passed_files/total_files*100:.1f}%")
    print()
    
    # Aggregate statistics
    if passed_files > 0:
        valid_metrics = [m for m in metrics_list if m.get('validation_passed', False)]
        
        total_vertices = sum(m.get('vertices', 0) for m in valid_metrics)
        total_faces = sum(m.get('faces', 0) for m in valid_metrics)
        total_volume = sum(m.get('volume', 0) for m in valid_metrics)
        total_size_mb = sum(m.get('file_size_mb', 0) for m in valid_metrics)
        
        print("📈 AGGREGATE STATISTICS")
        print(f"Total vertices: {total_vertices:,}")
        print(f"Total faces: {total_faces:,}")
        print(f"Total volume: {total_volume:.3f}")
        print(f"Total file size: {total_size_mb:.3f} MB")
        print()
        
        # Quality metrics
        watertight_count = sum(1 for m in valid_metrics if m.get('is_watertight', False))
        has_normals_count = sum(1 for m in valid_metrics if m.get('normals', {}).get('has_vertex_normals', False) or m.get('normals', {}).get('has_face_normals', False))
        
        print("🎯 QUALITY METRICS")
        print(f"Watertight meshes: {watertight_count}/{passed_files} ({watertight_count/passed_files*100:.1f}%)")
        print(f"Meshes with normals: {has_normals_count}/{passed_files} ({has_normals_count/passed_files*100:.1f}%)")
    
    # Failed files
    if failed_files > 0:
        print("\n❌ FAILED FILES")
        for metrics in metrics_list:
            if not metrics.get('validation_passed', False):
                print(f"  - {Path(metrics['file_path']).name}: {metrics.get('error', 'Unknown error')}")

def save_metrics(metrics_list, output_path="outputs/metrics.json"):
    """Save validation metrics to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Add timestamp and summary
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_files': len(metrics_list),
        'passed_files': sum(1 for m in metrics_list if m.get('validation_passed', False)),
        'failed_files': sum(1 for m in metrics_list if not m.get('validation_passed', False)),
        'metrics': metrics_list
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Metrics saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Validate 3D assets and generate metrics')
    parser.add_argument('path', help='Path to mesh file or directory to validate')
    parser.add_argument('--output', default='outputs/metrics.json', help='Output file for metrics')
    parser.add_argument('--verbose', action='store_true', help='Show detailed validation info')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    print("🔍 3D Asset Validation Tool")
    print("=" * 40)
    
    if path.is_file():
        # Validate single file
        metrics = validate_mesh(path)
        metrics_list = [metrics]
    elif path.is_dir():
        # Validate directory
        metrics_list = validate_directory(path)
    else:
        print(f"❌ Path not found: {path}")
        return 1
    
    if metrics_list:
        print_summary(metrics_list)
        save_metrics(metrics_list, args.output)
    
    # Return exit code based on validation results
    failed_count = sum(1 for m in metrics_list if not m.get('validation_passed', False))
    return 1 if failed_count > 0 else 0

if __name__ == "__main__":
    exit(main())
