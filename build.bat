@echo off
echo ============================================
echo   Building AutoBot for Claude Code .exe
echo ============================================
echo.

REM Install build dependencies
echo [1/3] Installing dependencies...
pip install pyinstaller pillow pyautogui winocr >nul 2>&1

REM Clean previous builds
echo [2/3] Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

REM Build
echo [3/3] Building with PyInstaller...
echo.
pyinstaller claude_code_auto_bot.spec

echo.
echo ============================================
if exist "dist\ClaudeCodeAutoBot.exe" (
    echo   BUILD SUCCESS
    echo   Output: dist\ClaudeCodeAutoBot.exe
    for %%A in ("dist\ClaudeCodeAutoBot.exe") do echo   Size: %%~zA bytes
) else (
    echo   BUILD FAILED - check output above
)
echo ============================================
echo.
pause
