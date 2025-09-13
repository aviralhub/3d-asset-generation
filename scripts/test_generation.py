#!/usr/bin/env python3
"""
Test script for 3D asset generation pipeline.
Uses detailed prompt and automatically validates outputs.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the generator
from src.generate import generate_asset_sync

def main():
    """Run generation test with detailed prompt and validation."""
    print("🚀 3D Asset Generation Test")
    print("=" * 50)
    
    # Detailed test prompt as specified
    detailed_prompt = (
        "A stylized sci-fi supply crate: rugged geometric panels, "
        "glowing cyan status panels recessed into the top and sides, "
        "reinforced riveted steel corners, small carry handle, "
        "low-poly game-ready stylization (clear silhouette), "
        "slightly worn paint chips on edges, no floating fragments, "
        "export-ready for Unity/Blender, balanced proportions."
    )
    
    # Test parameters as specified
    test_params = {
        "seed": 42,
        "steps": 20,
        "guidance_scale": 6.0
    }
    
    output_dir = "outputs/test_run"
    
    print(f"📝 Prompt: {detailed_prompt[:80]}...")
    print(f"⚙️  Parameters: {test_params}")
    print(f"📁 Output directory: {output_dir}")
    print()
    
    try:
        # Generate the asset
        print("🎨 Generating 3D asset...")
        result = generate_asset_sync(
            prompt=detailed_prompt,
            seed=test_params["seed"],
            steps=test_params["steps"],
            guidance_scale=test_params["guidance_scale"],
            output_dir=output_dir
        )
        
        print("✅ Generation successful!")
        print(f"   Job ID: {result['job_id']}")
        print(f"   Files created: {list(result['files'].values())}")
        print()
        
        # Automatically validate the output
        print("🔍 Running validation...")
        validation_result = validate_output(output_dir)
        
        if validation_result['success']:
            print("\n📊 Test Summary:")
            print(f"   Asset: {Path(validation_result['glb_path']).name}")
            print(f"   Vertices: {validation_result['vertex_count']}")
            print(f"   Faces: {validation_result['face_count']}")
            print(f"   Is watertight: {validation_result['is_watertight']}")
            print(f"   Volume: {validation_result['volume']:.3f}")
            print(f"   File size: {validation_result['metadata']['metrics']['file_size_mb']:.3f} MB")
            print()
            print("📋 Metadata Keys:")
            for key in validation_result['metadata'].keys():
                print(f"   - {key}")
            print()
            print("🎉 Test PASSED! Pipeline is working correctly.")
            return 0
        else:
            print(f"❌ Validation failed: {validation_result['error']}")
            return 1
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def validate_output(output_dir):
    """Validate the generated output using the validation script."""
    try:
        # Import and run the validation function
        from validate_output import validate_output as validate_func
        return validate_func(output_dir)
    except Exception as e:
        return {'success': False, 'error': f"Validation error: {str(e)}"}

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)