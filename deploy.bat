@echo off
title Quick Deploy to GitHub + Streamlit

cd /d "C:\Users\amith\Desktop\Assignments for MONEY\Dashboard - Rashika"

echo.
echo ==========================================
echo   DEPLOY: eea-biodiversity-dashboard
echo ==========================================
echo.

:: Check if there are any changes
git diff --quiet && git diff --cached --quiet
if %errorlevel%==0 (
    echo No changes detected. Nothing to deploy.
    echo.
    pause
    exit /b 0
)

:: Show what changed
echo Changes to be committed:
echo.
git status --short
echo.

:: Ask for commit message
set /p MSG="Commit message (press Enter for default): "
if "%MSG%"=="" set MSG=Update dashboard

:: Stage all, commit, push to main
git add .
git commit -m "%MSG%"

echo.
echo Pushing to GitHub main branch...
git push origin main

echo.
if %errorlevel%==0 (
    echo ==========================================
    echo   DONE - Streamlit will redeploy in ~60s
    echo   https://share.streamlit.io
    echo ==========================================
) else (
    echo Push failed. Check your internet or GitHub credentials.
)
echo.
pause
