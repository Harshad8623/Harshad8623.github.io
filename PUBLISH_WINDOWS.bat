@echo off
setlocal
cd /d "%~dp0"
echo =====================================================
echo    PUBLISH HARSHAD PORTFOLIO TO GITHUB PAGES
echo =====================================================
echo.
where git >nul 2>&1
if errorlevel 1 (echo ERROR: Git not installed. Install https://git-scm.com/ & pause & exit /b 1)
where gh >nul 2>&1
if errorlevel 1 (echo ERROR: GitHub CLI missing. Install https://cli.github.com/ & pause & exit /b 1)
gh auth status >nul 2>&1
if errorlevel 1 (echo Sign in first using: gh auth login & pause & exit /b 1)
for /f "tokens=*" %%i in ('gh api user --jq .login') do set "ACCOUNT=%%i"
if /I not "%ACCOUNT%"=="Harshad8623" (echo ERROR: Signed in as %ACCOUNT% but this package targets Harshad8623. & pause & exit /b 1)

gh repo view Harshad8623/Harshad8623.github.io >nul 2>&1
if not errorlevel 1 (
  echo Repository already exists. This script will not overwrite it.
  echo Follow README.md to update the existing site safely.
  pause
  exit /b 1
)

echo A new PUBLIC GitHub repository will be created under Harshad8623.
echo Only the files in this folder will be published.
echo Do NOT put secret keys, private resumes or .env files here.
echo.
set /p "CONFIRM=Type PUBLISH to create your public portfolio repository: "
if /I not "%CONFIRM%"=="PUBLISH" (echo Cancelled & pause & exit /b 0)

git init -b main
if errorlevel 1 (echo Could not initialize git repository & pause & exit /b 1)
git add -A
if errorlevel 1 (echo Could not add files & pause & exit /b 1)
git commit -m "Publish portfolio on GitHub Pages with Pages CMS"
if errorlevel 1 (echo Commit failed. Configure git user.name and user.email, then retry. & pause & exit /b 1)
gh repo create Harshad8623.github.io --public --source=. --remote=origin --push
if errorlevel 1 (echo GitHub repository creation or push failed. Check messages above. & pause & exit /b 1)
echo.
echo Repository pushed successfully.
echo NEXT: Open github.com/Harshad8623/Harshad8623.github.io/settings/pages
 echo Change Source to GitHub Actions, then open https://app.pagescms.org
 echo Read README.md for full steps.
pause
