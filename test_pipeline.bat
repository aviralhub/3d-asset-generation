@echo off
echo ========================================
echo 3D Asset Generation Pipeline Test
echo ========================================
echo.
echo This will run the complete end-to-end test:
echo  1. Generate a new 3D asset with detailed prompt
echo  2. Validate the generated GLB and metadata
echo  3. Open interactive visualization + save PNG snapshot
echo.
pause
echo.
echo Starting test...
python scripts/run_test.py
echo.
echo Test completed!
pause