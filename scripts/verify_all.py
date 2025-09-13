#!/usr/bin/env python3
"""
Comprehensive verification script for the 3D Asset Generation Pipeline.
Checks repo structure, runs tests, and validates outputs.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_repo_structure():
    """Check that all required files and directories exist."""
    print("🔍 Checking Repository Structure")
    print("=" * 40)
    
    required_files = [
        "src/generate.py",
        "src/model_loader.py", 
        "src/postprocess.py",
        "src/metrics.py",
        "src/api.py",
        "src/worker.py",
        "scripts/run_test.py",
        "scripts/test_generation.py",
        "scripts/validate_output.py",
        "scripts/visualize_output.py",
        "README.md",
        "experiments.md",
        "docs/writeup.md",
        "notebooks/demo_colab.ipynb",
        "requirements.txt",
        ".gitignore"
    ]
    
    required_dirs = [
        "src",
        "scripts", 
        "tests",
        "notebooks",
        "docs",
        "outputs"
    ]
    
    all_passed = True
    
    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ Directory: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            all_passed = False
    
    # Check files
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ File: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            all_passed = False
    
    print(f"\n📊 Structure Check: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

def run_pytest():
    """Run pytest and report results."""
    print("\n🧪 Running Unit Tests")
    print("=" * 40)
    
    try:
        # Run pytest with quiet output
        result = subprocess.run([sys.executable, "-m", "pytest", "-q"], 
                              capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print("❌ Some tests failed")
            print(f"Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ pytest failed to run: {e}")
        return False

def run_end_to_end_test():
    """Run the end-to-end test harness."""
    print("\n🚀 Running End-to-End Test")
    print("=" * 40)
    
    try:
        # Import and run the test
        from run_test import main as run_test_main
        result = run_test_main()
        
        if result == 0:
            print("✅ End-to-end test passed")
            return True
        else:
            print("❌ End-to-end test failed")
            return False
            
    except Exception as e:
        print(f"❌ End-to-end test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_fantasy_chest_test():
    """Run a test with the fantasy RPG treasure chest prompt."""
    print("\n🎮 Running Fantasy Chest Test")
    print("=" * 40)
    
    try:
        from test_fantasy_chest import main as run_fantasy_test
        
        print("📝 Using fantasy RPG treasure chest prompt...")
        
        result = run_fantasy_test()
        
        if result == 0:
            print("✅ Fantasy chest test passed")
            return True
        else:
            print("❌ Fantasy chest test failed")
            return False
            
    except Exception as e:
        print(f"❌ Fantasy chest test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_custom_test():
    """Run the custom test with medieval blacksmith's forge prompt."""
    print("\n🔨 Running Custom Test")
    print("=" * 40)
    
    try:
        from scripts.custom import main as run_custom_test_main
        
        print("📝 Using medieval blacksmith's forge prompt...")
        
        result = run_custom_test_main()
        
        if result == 0:
            print("✅ Custom test passed")
            return True
        else:
            print("❌ Custom test failed")
            return False
            
    except Exception as e:
        print(f"❌ Custom test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def inspect_outputs():
    """Inspect outputs in outputs/test_run/ directory."""
    print("\n📁 Inspecting Generated Outputs")
    print("=" * 40)
    
    output_dir = Path("outputs/test_run")
    if not output_dir.exists():
        print("❌ Output directory does not exist")
        return False
    
    # Find the latest job directory
    job_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
    if not job_dirs:
        print("❌ No job directories found")
        return False
    
    latest_job = max(job_dirs, key=lambda p: p.stat().st_mtime)
    print(f"📂 Latest job: {latest_job.name}")
    
    all_passed = True
    
    # Check for GLB file
    glb_file = latest_job / "main.glb"
    if glb_file.exists():
        print(f"✅ GLB file: {glb_file}")
        
        # Validate GLB with trimesh
        try:
            import trimesh
            loaded = trimesh.load(str(glb_file))
            
            # Handle Scene vs Mesh
            if isinstance(loaded, trimesh.Scene):
                print("⚠️  Scene detected, combining geometries...")
                geometries = list(loaded.geometry.values())
                mesh = trimesh.util.concatenate(geometries)
            else:
                mesh = loaded
            
            vertex_count = len(mesh.vertices)
            face_count = len(mesh.faces)
            
            print(f"   Vertices: {vertex_count}")
            print(f"   Faces: {face_count}")
            
            if vertex_count >= 10 and face_count >= 10:
                print("✅ GLB validation passed")
            else:
                print("❌ GLB validation failed: insufficient geometry")
                all_passed = False
                
        except Exception as e:
            print(f"❌ GLB validation error: {e}")
            all_passed = False
    else:
        print("❌ GLB file not found")
        all_passed = False
    
    # Check for screenshot
    screenshot_file = latest_job / "screenshot.png"
    if screenshot_file.exists():
        print(f"✅ Screenshot: {screenshot_file}")
    else:
        print("❌ Screenshot not found")
        all_passed = False
    
    # Check for metadata
    metadata_file = latest_job / "metadata.json"
    if metadata_file.exists():
        print(f"✅ Metadata: {metadata_file}")
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            required_keys = ['prompt', 'parameters', 'files', 'metrics', 'status']
            missing_keys = [key for key in required_keys if key not in metadata]
            
            if not missing_keys:
                print("✅ Metadata validation passed")
                print(f"   Status: {metadata['status']}")
                print(f"   Prompt length: {len(metadata['prompt'])} chars")
            else:
                print(f"❌ Metadata missing keys: {missing_keys}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Metadata validation error: {e}")
            all_passed = False
    else:
        print("❌ Metadata file not found")
        all_passed = False
    
    # Check for LOD files
    lod_files = list(latest_job.glob("lod*.glb"))
    if lod_files:
        print(f"✅ LOD files: {len(lod_files)} found")
    else:
        print("❌ LOD files not found")
        all_passed = False
    
    return all_passed, latest_job

def main():
    """Run complete verification suite."""
    print("🔍 3D Asset Generation Pipeline - Complete Verification")
    print("=" * 60)
    print("This will check:")
    print("  1. Repository structure")
    print("  2. Unit tests (pytest)")
    print("  3. End-to-end test harness")
    print("  4. Fantasy chest test example")
    print("  5. Custom test example")
    print("  6. Output validation")
    print("=" * 60)
    print()
    
    results = {}
    
    # Run all checks
    results['structure'] = check_repo_structure()
    results['pytest'] = run_pytest()
    results['end_to_end'] = run_end_to_end_test()
    results['fantasy_chest'] = run_fantasy_chest_test()
    results['custom'] = run_custom_test()
    results['outputs'], latest_job = inspect_outputs()
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎯 VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print(f"📊 Overall Result: {passed_checks}/{total_checks} checks passed")
    print()
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name.replace('_', ' ').title()}: {status}")
    
    print()
    
    if passed_checks == total_checks:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("   Your 3D asset generation pipeline is fully functional!")
        
        if latest_job:
            print(f"\n📁 Latest generated asset: {latest_job}")
            print(f"   GLB: {latest_job / 'main.glb'}")
            print(f"   Screenshot: {latest_job / 'screenshot.png'}")
            print(f"   Metadata: {latest_job / 'metadata.json'}")
    else:
        print("⚠️  SOME VERIFICATIONS FAILED!")
        print("   Please check the errors above and fix any issues.")
    
    return passed_checks == total_checks

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
