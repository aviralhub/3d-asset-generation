#!/usr/bin/env python3
"""
Test script for fantasy RPG treasure chest generation.
Uses the assignment-aligned prompt and validates outputs.
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
    """Run fantasy chest generation test."""
    print("🎮 Fantasy RPG Treasure Chest Generation Test")
    print("=" * 50)
    
    # Assignment-aligned fantasy chest prompt
    fantasy_prompt = (
        "A fantasy RPG treasure chest: ornate carved wood panels, "
        "reinforced gold trim, glowing rune engravings on the lid, "
        "slightly worn edges, game-ready low-poly with balanced proportions, "
        "no floating parts, export-ready for Unity/Blender."
    )
    
    # Test parameters
    test_params = {
        "seed": 123,  # Different seed for variety
        "steps": 25,  # More steps for better quality
        "guidance_scale": 7.0  # Higher guidance for more detail
    }
    
    output_dir = "outputs/test_run"
    
    print(f"📝 Prompt: {fantasy_prompt}")
    print(f"⚙️  Parameters: {test_params}")
    print(f"📁 Output directory: {output_dir}")
    print()
    
    try:
        # Generate the fantasy chest
        print("🎨 Generating fantasy treasure chest...")
        result = generate_asset_sync(
            prompt=fantasy_prompt,
            seed=test_params["seed"],
            steps=test_params["steps"],
            guidance_scale=test_params["guidance_scale"],
            output_dir=output_dir
        )
        
        print("✅ Fantasy chest generation successful!")
        print(f"   Job ID: {result['job_id']}")
        print(f"   Files created: {list(result['files'].values())}")
        print()
        
        # Validate the output
        print("🔍 Running validation...")
        validation_result = validate_output(output_dir)
        
        if validation_result['success']:
            print("\n📊 Fantasy Chest Summary:")
            print(f"   Asset: {Path(validation_result['glb_path']).name}")
            print(f"   Vertices: {validation_result['vertex_count']}")
            print(f"   Faces: {validation_result['face_count']}")
            print(f"   Is watertight: {validation_result['is_watertight']}")
            print(f"   Volume: {validation_result['volume']:.3f}")
            print(f"   File size: {validation_result['metadata']['metrics']['file_size_mb']:.3f} MB")
            print()
            print("📋 Generated Files:")
            print(f"   GLB: {validation_result['glb_path']}")
            print(f"   Screenshot: {Path(validation_result['glb_path']).parent / 'screenshot.png'}")
            print(f"   Metadata: {Path(validation_result['glb_path']).parent / 'metadata.json'}")
            print()
            print("🎉 Fantasy chest test PASSED!")
            return 0
        else:
            print(f"❌ Validation failed: {validation_result['error']}")
            return 1
            
    except Exception as e:
        print(f"❌ Fantasy chest generation failed: {e}")
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
