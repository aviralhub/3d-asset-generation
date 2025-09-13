# Custom Testing Guide

## Overview
The `custom.py` script allows you to test the 3D asset generation pipeline with your own creative prompts and parameters.

## Usage

### Run Custom Test
```bash
python scripts/custom.py
```

### Or use the batch file (Windows)
```bash
test_custom.bat
```

## What It Does

1. **Generates** a medieval blacksmith's forge with:
   - Stone base with glowing embers
   - Iron anvil on top
   - Wooden tool rack with hammers and tongs
   - Low-poly stylized for RPG game
   - Balanced proportions, export-ready for Unity/Blender

2. **Parameters Used**:
   - seed: 999
   - steps: 30
   - guidance_scale: 7.5

3. **Outputs**:
   - Saves to `outputs/custom_test/`
   - Creates GLB model, LODs, screenshot, and metadata
   - Validates the generated asset
   - Prints detailed results

## Customization

To modify the test:

1. Edit `scripts/custom.py`
2. Change the `prompt` variable for different assets
3. Modify the `params` dictionary for different generation settings
4. Run the script

## Integration

The custom test is integrated into the main verification suite:
```bash
python scripts/verify_all.py
```

This will run all tests including the custom test.

## Output Files

Generated assets are saved in:
```
outputs/custom_test/[job_id]/
├── main.glb          # Main 3D model
├── lod1.glb          # Level of detail 1
├── lod2.glb          # Level of detail 2
├── screenshot.png    # Visual preview
└── metadata.json     # Generation details
```

## Example Results

The custom test generates assets with:
- 162 vertices
- 320 faces
- Watertight geometry
- Complete metadata
- All required files (GLB, LODs, screenshot)

## Troubleshooting

If the custom test fails:
1. Check that all dependencies are installed
2. Ensure the generator is working (run other tests first)
3. Check the error messages in the output
4. Verify file permissions for the outputs directory
