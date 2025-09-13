#!/usr/bin/env python3
"""
Validation script for generated 3D assets.
Handles both trimesh.Trimesh and trimesh.Scene objects.
"""

import trimesh
import json
import os
from pathlib import Path

def find_latest_glb(output_dir="outputs/test_run"):
    """Find the latest GLB file in the output directory structure."""
    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")
    
    # Look for GLB files in subdirectories (job_id folders)
    glb_files = []
    for subdir in output_path.iterdir():
        if subdir.is_dir():
            main_glb = subdir / "main.glb"
            if main_glb.exists():
                glb_files.append(main_glb)
    
    if not glb_files:
        raise FileNotFoundError(f"No GLB files found in {output_dir}")
    
    # Return the most recently modified
    return max(glb_files, key=lambda p: p.stat().st_mtime)

def validate_output(output_dir="outputs/test_run"):
    """Validate the latest generated GLB file and metadata."""
    print("🔍 Validating Generated Asset")
    print("=" * 40)
    
    try:
        # Find the latest GLB file
        glb_path = find_latest_glb(output_dir)
        print(f"📁 Found: {glb_path.name}")
        
        # Load the mesh
        print("🔄 Loading GLB...")
        loaded = trimesh.load(str(glb_path))
        
        # Handle Scene vs Trimesh
        if isinstance(loaded, trimesh.Scene):
            print("⚠️  Scene detected, combining geometries...")
            if len(loaded.geometry) == 0:
                raise ValueError("Scene has no geometry")
            
            # Combine all geometries into a single mesh
            geometries = list(loaded.geometry.values())
            mesh = trimesh.util.concatenate(geometries)
            print(f"   Combined {len(geometries)} geometries")
        else:
            mesh = loaded
            print("✅ Loaded as single mesh")
        
        # Validate mesh properties
        vertex_count = len(mesh.vertices)
        face_count = len(mesh.faces)
        is_watertight = mesh.is_watertight
        volume = mesh.volume if hasattr(mesh, 'volume') else 0.0
        surface_area = mesh.surface_area if hasattr(mesh, 'surface_area') else 0.0
        
        print(f"\n📊 Mesh Properties:")
        print(f"   Vertices: {vertex_count}")
        print(f"   Faces: {face_count}")
        print(f"   Is watertight: {is_watertight}")
        print(f"   Volume: {volume:.3f}")
        print(f"   Surface area: {surface_area:.3f}")
        
        # Basic sanity check
        if vertex_count < 10:
            raise ValueError(f"Too few vertices: {vertex_count} < 10")
        if face_count < 10:
            raise ValueError(f"Too few faces: {face_count} < 10")
        
        # Load and validate metadata
        metadata_path = glb_path.parent / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        print(f"\n📄 Loading metadata...")
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Print all metadata keys and values
        print("📋 Metadata Contents:")
        for key, value in metadata.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for subkey, subvalue in value.items():
                    print(f"     {subkey}: {subvalue}")
            else:
                print(f"   {key}: {value}")
        
        # Validate metadata structure
        required_fields = ['job_id', 'prompt', 'parameters', 'files', 'metrics', 'status']
        missing_fields = [field for field in required_fields if field not in metadata]
        if missing_fields:
            raise ValueError(f"Missing required metadata fields: {missing_fields}")
        
        if metadata['status'] != 'completed':
            raise ValueError(f"Generation not completed: status = {metadata['status']}")
        
        print("\n🎉 Validation successful!")
        print("   ✅ GLB file loads correctly")
        print("   ✅ Mesh has valid geometry")
        print("   ✅ Metadata is complete")
        
        return {
            'success': True,
            'glb_path': str(glb_path),
            'vertex_count': vertex_count,
            'face_count': face_count,
            'is_watertight': is_watertight,
            'volume': volume,
            'surface_area': surface_area,
            'metadata': metadata
        }
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    validate_output()