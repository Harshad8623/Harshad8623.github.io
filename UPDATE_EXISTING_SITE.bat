@echo off
setlocal
cd /d "%~dp0"
echo ============================================
echo    HARSHAD PORTFOLIO V3 SAFE UPDATE
echo ============================================
echo This script PRESERVES existing CMS content,
echo projects, resumes, certificates and uploads.
echo It creates a full Git backup before changing anything.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0UPDATE_EXISTING_SITE.ps1"
echo.
pause
