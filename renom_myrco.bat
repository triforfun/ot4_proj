@echo off
python c:/soft_proj/ot4_proj/renom_myrco.py
if %errorlevel% neq 0 (
    echo An error occurred while running renom_myrco.py
    exit /b %errorlevel%
)
echo renom_myrco.py executed successfully