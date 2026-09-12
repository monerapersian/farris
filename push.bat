@echo off
setlocal

echo ===================================
echo   Git Push Script - Farris Project
echo ===================================
echo.

cd /d "%~dp0"

echo Under review
git status
echo.

set /p commitMsg="Enter your commit: "

if "%commitMsg%"=="" (
    echo payam commit nemitone khali bashe
    pause
    exit /b
)

git add .
git commit -m "%commitMsg%"
git push

echo.
echo ===================================
echo   Done.
echo ===================================
pause