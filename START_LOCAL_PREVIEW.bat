@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (py -3 scripts\build.py) else (python scripts\build.py)
if errorlevel 1 (echo Build failed. & pause & exit /b 1)
echo Opening http://127.0.0.1:8000 ...
start "" http://127.0.0.1:8000
where py >nul 2>&1
if %errorlevel%==0 (py -3 -m http.server 8000 --directory dist) else (python -m http.server 8000 --directory dist)
pause
