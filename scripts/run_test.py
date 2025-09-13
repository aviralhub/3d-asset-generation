#!/usr/bin/env python3
"""
End-to-End Test Harness for 3D Asset Generation Pipeline.
Runs generation, validation, and visualization in sequence.
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Run complete end-to-end test pipeline."""
    print("🚀 3D Asset Generation Pipeline - End-to-End Test")
    print("=" * 60)
    print("This will:")
    print("  1. Generate a new 3D asset with detailed prompt")
    print("  2. Validate the generated GLB and metadata")
    print("  3. Open interactive visualization + save PNG snapshot")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Run generation test
        print("📋 Step 1: Generation Test")
        print("-" * 30)
        
        from test_generation import main as run_generation
        generation_result = run_generation()
        
        if generation_result != 0:
            print("❌ Generation test failed!")
            return 1
        
        print("\n✅ Generation successful")
        print()
        
        # Step 2: Run validation
        print("📋 Step 2: Validation Test")
        print("-" * 30)
        
        from validate_output import validate_output
        validation_result = validate_output()
        
        if not validation_result['success']:
            print("❌ Validation test failed!")
            return 1
        
        print("\n✅ Validation successful")
        print()
        
        # Step 3: Run visualization
        print("📋 Step 3: Visualization Test")
        print("-" * 30)
        
        from visualize_output import visualize_output
        visualization_result = visualize_output()
        
        if not visualization_result:
            print("❌ Visualization test failed!")
            return 1
        
        print("\n🎉 Visualization shown")
        print()
        
        # Final summary with all details
        print("🎉 END-TO-END TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Generation successful")
        print("✅ Validation successful")
        print("🎉 Visualization shown")
        print()
        print("📊 Final Results:")
        print(f"   Vertices: {validation_result['vertex_count']}")
        print(f"   Faces: {validation_result['face_count']}")
        print(f"   Is watertight: {validation_result['is_watertight']}")
        print(f"   Volume: {validation_result['volume']:.3f}")
        print(f"   Surface area: {validation_result['surface_area']:.3f}")
        print()
        print("📋 Metadata Keys:")
        for key in validation_result['metadata'].keys():
            print(f"   - {key}")
        print()
        print("🚀 Your 3D asset generation pipeline is fully functional!")
        print("   - Generates GLB models from text prompts")
        print("   - Creates LODs, screenshots, and metadata")
        print("   - Validates mesh quality and completeness")
        print("   - Provides interactive visualization + PNG snapshots")
        print()
        print("📁 Check outputs/test_run/ for generated assets")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def run_generation_and_validation(prompt, output_dir="outputs/custom_test", params=None):
    """
    Run generation and validation for custom prompts.
    This function is used by custom.py and other test scripts.
    """
    if params is None:
        params = {"seed": 42, "steps": 20, "guidance_scale": 6.0}
    
    try:
        # Import the generator
        from src.generate import generate_asset_sync
        
        print(f"🎨 Generating custom asset...")
        print(f"📝 Prompt: {prompt[:80]}...")
        print(f"⚙️  Parameters: {params}")
        
        # Generate the asset
        result = generate_asset_sync(
            prompt=prompt,
            seed=params["seed"],
            steps=params["steps"],
            guidance_scale=params["guidance_scale"],
            output_dir=output_dir
        )
        
        print("✅ Custom generation successful!")
        print(f"   Job ID: {result['job_id']}")
        
        # Validate the output
        from validate_output import validate_output as validate_func
        validation_result = validate_func(output_dir)
        
        if validation_result['success']:
            return {
                "status": "success",
                "job_id": result['job_id'],
                "vertex_count": validation_result['vertex_count'],
                "face_count": validation_result['face_count'],
                "is_watertight": validation_result['is_watertight'],
                "volume": validation_result['volume'],
                "file_size_mb": validation_result['metadata']['metrics']['file_size_mb'],
                "glb_path": validation_result['glb_path'],
                "screenshot_path": str(Path(validation_result['glb_path']).parent / "screenshot.png"),
                "metadata_path": str(Path(validation_result['glb_path']).parent / "metadata.json")
            }
        else:
            return {
                "status": "validation_failed",
                "error": validation_result['error'],
                "job_id": result['job_id']
            }
            
    except Exception as e:
        return {
            "status": "generation_failed",
            "error": str(e)
        }

def show_help():
    """Show help information."""
    print("3D Asset Generation Pipeline - Test Harness")
    print("=" * 50)
    print()
    print("Usage:")
    print("  python scripts/run_test.py")
    print()
    print("This script will:")
    print("  1. Generate a sci-fi supply crate from detailed prompt")
    print("  2. Validate the generated GLB file and metadata")
    print("  3. Open an interactive 3D viewer + save PNG snapshot")
    print()
    print("Requirements:")
    print("  - trimesh (required)")
    print("  - pyrender (optional, for better visualization)")
    print("  - matplotlib (optional, for PNG snapshots)")
    print()
    print("Output:")
    print("  - Generated assets saved to outputs/test_run/")
    print("  - Interactive 3D viewer opens automatically")
    print("  - PNG snapshot saved in asset folder")
    print("  - Detailed validation results printed")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
    else:
        exit_code = main()
        sys.exit(exit_code)