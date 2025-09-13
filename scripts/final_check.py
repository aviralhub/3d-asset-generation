#!/usr/bin/env python3
"""
Final End-to-End Check Script for 3D Asset Pipeline.
Generates with a custom prompt, validates results,
runs visualization, and prints a clean summary.
"""

import os
import sys
import datetime
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import pipeline pieces
from src.generate import generate_asset_sync


def main():
    print("\n FINAL END-TO-END PIPELINE CHECK")
    print("=" * 60)

    # Final showcase prompt (edit if needed)
    final_prompt = (
        "A magical ancient book on a stone pedestal, "
        "with glowing runes floating above, "
        "chains wrapped around the sides, "
        "low-poly stylized for RPG, balanced proportions, "
        "ready for Unity/Blender."
    )

    final_params = {
        "seed": 42,
        "steps": 28,
        "guidance_scale": 7.0
    }

    # Unique timestamped output dir
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"outputs/final_check_{run_id}"
    os.makedirs(output_dir, exist_ok=True)

    print(f" Prompt: {final_prompt}")
    print(f" Parameters: {final_params}")
    print(f" Output directory: {output_dir}\n")

    try:
        # Step 1: Generate
        print("🎨 Generating final asset...")
        result = generate_asset_sync(
            prompt=final_prompt,
            seed=final_params["seed"],
            steps=final_params["steps"],
            guidance_scale=final_params["guidance_scale"],
            output_dir=output_dir
        )

        print(" Generation successful!")
        print(f"   Job ID: {result['job_id']}")
        print(f"   Files created: {list(result['files'].values())}\n")

        # Step 2: Validation
        print(" Validating output...")
        validation_result = validate_output(output_dir)

        if validation_result["success"]:
            print("\n FINAL CHECK SUMMARY")
            print("=" * 60)
            print(f"   Asset: {Path(validation_result['glb_path']).name}")
            print(f"   Vertices: {validation_result['vertex_count']}")
            print(f"   Faces: {validation_result['face_count']}")
            print(f"   Watertight: {validation_result['is_watertight']}")
            print(f"   Volume: {validation_result['volume']:.3f}")
            print(f"   File size: {validation_result['metadata']['metrics']['file_size_mb']:.3f} MB")
            print("\n Files saved:")
            print(f"   GLB: {validation_result['glb_path']}")
            print(f"   Screenshot: {Path(output_dir) / 'screenshot.png'}")
            print(f"   Metadata: {Path(output_dir) / 'metadata.json'}")

            # Step 3: Visualization
            print("\n Launching visualization...")
            try:
                from visualize_output import visualize_output
                if visualize_output(output_dir):
                    print(" Visualization completed")
                else:
                    print(" Visualization failed, but generation OK")
            except Exception as e:
                print(f" Visualization error: {e}")

            print("\n🎉 FINAL PIPELINE CHECK PASSED!\n")
            return 0

        else:
            print(f"❌ Validation failed: {validation_result['error']}")
            return 1

    except Exception as e:
        print(f"❌ Final check failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def validate_output(output_dir):
    """Wrapper for validation script."""
    try:
        from validate_output import validate_output as validate_func
        return validate_func(output_dir)
    except Exception as e:
        return {"success": False, "error": f"Validation error: {str(e)}"}


if __name__ == "__main__":
    sys.exit(main())
