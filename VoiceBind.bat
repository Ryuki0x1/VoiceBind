@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === VoiceBind — Push to GitHub ===
echo.

if not exist .git (
    git init
    echo [OK] Git repo initialized.
)

git add .
git commit -m "Initial commit" 2>nul

set /p TOKEN=GitHub token (repo scope): 

git remote remove origin 2>nul
git remote add origin https://%TOKEN%@github.com/Ryuki0x1/VoiceBind.git
git branch -M main
git push -f origin main

if %errorlevel% equ 0 (
    echo [OK] Pushed!
    git remote set-url origin https://github.com/Ryuki0x1/VoiceBind.git
    echo [OK] Token removed from remote URL.
) else (
    echo [FAIL] Push failed.
)

pause
