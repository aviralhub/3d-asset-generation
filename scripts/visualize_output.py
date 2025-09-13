#!/usr/bin/env python3
"""
Visualization script for generated 3D assets.
Opens an interactive viewer and saves PNG snapshot.
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import trimesh
    import numpy as np
except ImportError:
    print("❌ Error: trimesh not installed. Run: pip install trimesh")
    sys.exit(1)

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

def save_png_snapshot(mesh, output_path):
    """Save a PNG snapshot of the mesh or scene."""
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        if len(mesh.vertices) == 0:
            raise ValueError("Mesh has no vertices to render")

        print("📸 Creating PNG snapshot...")

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")

        vertices = mesh.vertices
        faces = mesh.faces if hasattr(mesh, "faces") else []

        if faces is not None and len(faces) > 0:
            # Normal surface rendering
            ax.plot_trisurf(
                vertices[:, 0], vertices[:, 1], vertices[:, 2],
                triangles=faces,
                alpha=0.8, color="lightblue",
                edgecolor="navy", linewidth=0.3
            )
        else:
            # Fallback to scatter if no faces
            ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2],
                       c="blue", s=1, alpha=0.6)
            print("⚠️ No faces detected, plotted as point cloud instead.")

        # Equal aspect ratio
        max_range = np.array([
            vertices[:, 0].max() - vertices[:, 0].min(),
            vertices[:, 1].max() - vertices[:, 1].min(),
            vertices[:, 2].max() - vertices[:, 2].min()
        ]).max() / 2.0
        mid_x = (vertices[:, 0].max() + vertices[:, 0].min()) * 0.5
        mid_y = (vertices[:, 1].max() + vertices[:, 1].min()) * 0.5
        mid_z = (vertices[:, 2].max() + vertices[:, 2].min()) * 0.5

        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)

        ax.set_title("Generated 3D Asset Snapshot")

        # Save
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"✅ PNG snapshot saved: {output_path}")
        return True

    except Exception as e:
        print(f"❌ PNG snapshot failed: {e}")
        return False

def visualize_with_pyrender(mesh):
    """Visualize mesh using pyrender (preferred option)."""
    try:
        import pyrender
        
        print("🎮 Creating pyrender visualization...")
        
        # Create scene
        scene = pyrender.Scene()
        
        # Add mesh to scene
        mesh_node = scene.add(pyrender.Mesh.from_trimesh(mesh))
        
        # Add camera
        camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
        camera_pose = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 3.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
        scene.add(camera, pose=camera_pose)
        
        # Add lighting
        light = pyrender.SpotLight(color=np.ones(3), intensity=3.0,
                                   innerConeAngle=np.pi/16.0,
                                   outerConeAngle=np.pi/6.0)
        scene.add(light, pose=camera_pose)
        
        # Create viewer
        viewer = pyrender.Viewer(scene, use_raymond_lighting=True)
        
        print("✅ pyrender visualization completed")
        return True
        
    except ImportError:
        print("⚠️  pyrender not available, trying matplotlib...")
        return False
    except Exception as e:
        print(f"❌ pyrender visualization failed: {e}")
        return False

def visualize_with_matplotlib(mesh):
    """Visualize mesh using matplotlib (fallback option)."""
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        print("📊 Creating matplotlib visualization...")
        
        # Create figure
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot the mesh
        vertices = mesh.vertices
        faces = mesh.faces
        
        ax.plot_trisurf(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
                        triangles=faces, alpha=0.7, color='lightblue', 
                        edgecolor='navy', linewidth=0.5)
        
        # Labels + title
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Generated 3D Asset Preview')
        
        # Equal aspect ratio
        max_range = np.array([vertices[:, 0].max() - vertices[:, 0].min(),
                             vertices[:, 1].max() - vertices[:, 1].min(),
                             vertices[:, 2].max() - vertices[:, 2].min()]).max() / 2.0
        mid_x = (vertices[:, 0].max() + vertices[:, 0].min()) * 0.5
        mid_y = (vertices[:, 1].max() + vertices[:, 1].min()) * 0.5
        mid_z = (vertices[:, 2].max() + vertices[:, 2].min()) * 0.5
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        print("🖼️  Opening matplotlib viewer...")
        plt.show()
        return True
        
    except ImportError:
        print("⚠️  matplotlib not available for visualization")
        return False
    except Exception as e:
        print(f"❌ matplotlib visualization failed: {e}")
        return False

def visualize_output(output_dir="outputs/test_run"):
    """Visualize the latest generated GLB file and save PNG snapshot."""
    print("🎨 3D Asset Visualization")
    print("=" * 40)
    
    try:
        # Find the latest GLB file
        glb_path = find_latest_glb(output_dir)
        print(f"📁 Loading: {glb_path.name}")
        
        # Load mesh
        print("🔄 Loading GLB file...")
        loaded = trimesh.load(str(glb_path))
        
        if isinstance(loaded, trimesh.Scene):
            print("⚠️  Scene detected, combining geometries...")
            if len(loaded.geometry) == 0:
                raise ValueError("Scene has no geometry")
            geometries = list(loaded.geometry.values())
            mesh = trimesh.util.concatenate(geometries)
            print(f"   Combined {len(geometries)} geometries")
        else:
            mesh = loaded
            print("✅ Loaded as single mesh")
        
        # Mesh info
        print(f"\n📊 Mesh Info:")
        print(f"   Vertices: {len(mesh.vertices)}")
        print(f"   Faces: {len(mesh.faces)}")
        print(f"   Is watertight: {mesh.is_watertight}")
        
        # Save PNG snapshot (two places)
        job_id = glb_path.parent.name
        
        # 1. Next to GLB
        local_snapshot = glb_path.parent / "visualization_snapshot.png"
        save_png_snapshot(mesh, local_snapshot)
        
        # 2. Central screenshots folder
        screenshots_dir = Path("outputs/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        central_snapshot = screenshots_dir / f"{job_id}_snapshot.png"
        save_png_snapshot(mesh, central_snapshot)
        
        # Try visualization methods
        print(f"\n🖼️  Opening interactive viewer...")
        if visualize_with_pyrender(mesh):
            return True
        if visualize_with_matplotlib(mesh):
            return True
        
        print("⚠️  No interactive visualization available, but mesh loaded successfully")
        print(f"   Snapshots available: {local_snapshot}, {central_snapshot}")
        return True
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = visualize_output()
    if success:
        print("\n🎉 Visualization completed!")
    else:
        print("\n❌ Visualization failed!")
        sys.exit(1)
