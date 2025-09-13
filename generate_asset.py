#!/usr/bin/env python3
"""
Asset Generation Script for 3D Game Assets
Generates multiple shapes (cube, cone, icosphere, noisy stone) with parameter control.
"""

import argparse
import os
import json
import numpy as np
import trimesh
from pathlib import Path
from datetime import datetime

def generate_cube(size=1.0, subdivisions=0):
    """Generate a cube with optional subdivisions."""
    return trimesh.creation.box(extents=[size, size, size])

def generate_cone(radius=1.0, height=2.0, subdivisions=8):
    """Generate a cone with specified radius, height, and subdivisions."""
    return trimesh.creation.cone(radius=radius, height=height, sections=subdivisions)

def generate_icosphere(radius=1.0, subdivisions=2):
    """Generate an icosphere with specified radius and subdivisions."""
    return trimesh.creation.icosphere(radius=radius, subdivisions=subdivisions)

def generate_noisy_stone(radius=1.0, noise_scale=0.1, subdivisions=2, seed=None):
    """Generate a stone-like object with noise applied."""
    if seed is not None:
        np.random.seed(seed)
    
    # Start with an icosphere
    mesh = trimesh.creation.icosphere(radius=radius, subdivisions=subdivisions)
    
    # Add noise to vertices for stone-like appearance
    noise = np.random.normal(0, noise_scale, mesh.vertices.shape)
    mesh.vertices += noise
    
    # Recompute normals after noise
    mesh.compute_vertex_normals()
    
    return mesh

def generate_torus(major_radius=1.0, minor_radius=0.3, subdivisions=8):
    """Generate a torus with specified radii and subdivisions."""
    return trimesh.creation.torus(major_radius=major_radius, minor_radius=minor_radius, sections=subdivisions)

def save_asset(mesh, name, output_dir="outputs/assets", save_obj=True, save_glb=True, save_screenshot=True):
    """Save mesh in multiple formats."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save GLB
    if save_glb:
        glb_path = output_path / f"{name}.glb"
        mesh.export(str(glb_path))
        saved_files['glb'] = str(glb_path)
        print(f"✅ Saved GLB: {glb_path}")
    
    # Save OBJ
    if save_obj:
        obj_path = output_path / f"{name}.obj"
        mesh.export(str(obj_path))
        saved_files['obj'] = str(obj_path)
        print(f"✅ Saved OBJ: {obj_path}")
    
    # Save screenshot
    if save_screenshot:
        screenshot_path = Path("outputs/screenshots")
        screenshot_path.mkdir(parents=True, exist_ok=True)
        
        # Create a simple scene for screenshot
        scene = trimesh.Scene([mesh])
        screenshot_file = screenshot_path / f"{name}_screenshot.png"
        
        try:
            # Try to save screenshot (may not work in headless environments)
            scene.save_image(str(screenshot_file), resolution=(512, 512))
            saved_files['screenshot'] = str(screenshot_file)
            print(f"✅ Saved screenshot: {screenshot_file}")
        except Exception as e:
            print(f"⚠️  Could not save screenshot: {e}")
    
    return saved_files

def get_mesh_info(mesh):
    """Get basic information about the mesh."""
    return {
        'vertices': len(mesh.vertices),
        'faces': len(mesh.faces),
        'edges': len(mesh.edges),
        'is_watertight': mesh.is_watertight,
        'volume': float(mesh.volume) if hasattr(mesh, 'volume') else 0.0,
        'surface_area': float(mesh.surface_area) if hasattr(mesh, 'surface_area') else 0.0,
        'bounding_box': {
            'min': mesh.bounds[0].tolist(),
            'max': mesh.bounds[1].tolist(),
            'size': (mesh.bounds[1] - mesh.bounds[0]).tolist()
        },
        'has_vertex_normals': hasattr(mesh, 'vertex_normals') and mesh.vertex_normals is not None,
        'has_face_normals': hasattr(mesh, 'face_normals') and mesh.face_normals is not None
    }

def main():
    parser = argparse.ArgumentParser(description='Generate 3D assets for games')
    parser.add_argument('--shape', choices=['cube', 'cone', 'icosphere', 'stone', 'torus'], 
                       default='cube', help='Shape to generate')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducible generation')
    parser.add_argument('--radius', type=float, default=1.0, help='Radius parameter')
    parser.add_argument('--height', type=float, default=2.0, help='Height parameter (for cone)')
    parser.add_argument('--subdivisions', type=int, default=2, help='Subdivision level')
    parser.add_argument('--noise-scale', type=float, default=0.1, help='Noise scale for stone generation')
    parser.add_argument('--size', type=float, default=1.0, help='Size parameter (for cube)')
    parser.add_argument('--minor-radius', type=float, default=0.3, help='Minor radius (for torus)')
    parser.add_argument('--output-dir', default='outputs/assets', help='Output directory')
    parser.add_argument('--name', help='Custom name for the asset (default: shape_timestamp)')
    
    args = parser.parse_args()
    
    # Set random seed
    np.random.seed(args.seed)
    
    print(f"🎨 Generating {args.shape} asset...")
    print(f"📊 Parameters: seed={args.seed}, radius={args.radius}, subdivisions={args.subdivisions}")
    
    # Generate mesh based on shape
    if args.shape == 'cube':
        mesh = generate_cube(size=args.size, subdivisions=args.subdivisions)
    elif args.shape == 'cone':
        mesh = generate_cone(radius=args.radius, height=args.height, subdivisions=args.subdivisions)
    elif args.shape == 'icosphere':
        mesh = generate_icosphere(radius=args.radius, subdivisions=args.subdivisions)
    elif args.shape == 'stone':
        mesh = generate_noisy_stone(radius=args.radius, noise_scale=args.noise_scale, 
                                  subdivisions=args.subdivisions, seed=args.seed)
    elif args.shape == 'torus':
        mesh = generate_torus(major_radius=args.radius, minor_radius=args.minor_radius, 
                            subdivisions=args.subdivisions)
    
    # Generate name if not provided
    if not args.name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.name = f"{args.shape}_{timestamp}"
    
    # Save asset
    saved_files = save_asset(mesh, args.name, args.output_dir)
    
    # Get mesh information
    mesh_info = get_mesh_info(mesh)
    mesh_info['parameters'] = vars(args)
    mesh_info['saved_files'] = saved_files
    
    # Save metadata
    metadata_path = Path(args.output_dir) / f"{args.name}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(mesh_info, f, indent=2)
    
    print(f"\n📊 Asset Information:")
    print(f"   Vertices: {mesh_info['vertices']}")
    print(f"   Faces: {mesh_info['faces']}")
    print(f"   Is watertight: {mesh_info['is_watertight']}")
    print(f"   Volume: {mesh_info['volume']:.3f}")
    print(f"   Surface area: {mesh_info['surface_area']:.3f}")
    print(f"   Has vertex normals: {mesh_info['has_vertex_normals']}")
    print(f"   Has face normals: {mesh_info['has_face_normals']}")
    
    print(f"\n🎉 Asset generation complete!")
    print(f"📁 Files saved: {list(saved_files.values())}")
    print(f"📄 Metadata: {metadata_path}")

if __name__ == "__main__":
    main()
