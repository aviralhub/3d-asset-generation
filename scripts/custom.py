#!/usr/bin/env python3
"""
Custom test script for 3D asset generation pipeline.
Uses your custom prompts and automatically validates outputs.
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
    """Run custom generation test with your prompts."""
    print(" Custom 3D Asset Generation Test")
    print("=" * 50)
    
    # Your custom prompt
    custom_prompt = (
        "A cat sword, "
        "stone base with glowing embers, iron anvil on top, "
        "wooden tool rack with hammers and tongs, "
        "low-poly stylized for RPG game, balanced proportions, "
        "export-ready for Unity/Blender."
    )
    
    # Custom parameters
    custom_params = {
        "seed": 999,
        "steps": 30,
        "guidance_scale": 7.5
    }
    
    output_dir = "outputs/custom_test"
    
    print(f" Prompt: {custom_prompt}")
    print(f"  Parameters: {custom_params}")
    print(f" Output directory: {output_dir}")
    print()
    
    try:
        # Generate the custom asset
        print("🎨 Generating custom asset...")
        result = generate_asset_sync(
            prompt=custom_prompt,
            seed=custom_params["seed"],
            steps=custom_params["steps"],
            guidance_scale=custom_params["guidance_scale"],
            output_dir=output_dir
        )
        
        print(" Custom generation successful!")
        print(f"   Job ID: {result['job_id']}")
        print(f"   Files created: {list(result['files'].values())}")
        print()
        
        # Automatically validate the output
        print(" Running validation...")
        validation_result = validate_output(output_dir)
        
        if validation_result['success']:
            print("\n Custom Test Summary:")
            print(f"   Asset: {Path(validation_result['glb_path']).name}")
            print(f"   Vertices: {validation_result['vertex_count']}")
            print(f"   Faces: {validation_result['face_count']}")
            print(f"   Is watertight: {validation_result['is_watertight']}")
            print(f"   Volume: {validation_result['volume']:.3f}")
            print(f"   File size: {validation_result['metadata']['metrics']['file_size_mb']:.3f} MB")
            print()
            print(" Generated Files:")
            print(f"   GLB: {validation_result['glb_path']}")
            print(f"   Screenshot: {Path(validation_result['glb_path']).parent / 'screenshot.png'}")
            print(f"   Metadata: {Path(validation_result['glb_path']).parent / 'metadata.json'}")
            print()
            
            # Run visualization
            print("🎨 Running visualization...")
            try:
                from visualize_output import visualize_output
                visualization_result = visualize_output(output_dir)
                if visualization_result:
                    print("✅ Visualization completed")
                else:
                    print("⚠️  Visualization failed but generation was successful")
            except Exception as e:
                print(f"⚠️  Visualization error: {e}")
            
            print("\n🎉 Custom test PASSED!")
            return 0
        else:
            print(f"❌ Validation failed: {validation_result['error']}")
            return 1
            
    except Exception as e:
        print(f"❌ Custom generation failed: {e}")
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