@echo off
echo ========================================
echo Custom 3D Asset Generation Test
echo ========================================
echo.
echo This will generate a medieval blacksmith's forge:
echo   - Stone base with glowing embers
echo   - Iron anvil on top
echo   - Wooden tool rack with hammers and tongs
echo   - Low-poly stylized for RPG game
echo   - Balanced proportions, export-ready for Unity/Blender
echo.
echo Parameters: seed=999, steps=30, guidance_scale=7.5
echo.
pause
echo.
echo Starting custom test...
python scripts/custom.py
echo.
echo Custom test completed!
echo Check outputs/custom_test/ for generated files
pause
