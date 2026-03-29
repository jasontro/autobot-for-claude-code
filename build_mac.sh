#!/bin/bash
echo "============================================"
echo "  Building Claude Code Auto-Bot .app"
echo "============================================"
echo

# Install build dependencies
echo "[1/3] Installing dependencies..."
pip install pyinstaller pillow pyautogui pytesseract 2>/dev/null

# Clean previous builds
echo "[2/3] Cleaning previous builds..."
rm -rf build dist

# Build
echo "[3/3] Building with PyInstaller..."
echo
pyinstaller claude_code_auto_bot_mac.spec

echo
echo "============================================"
if [ -d "dist/ClaudeCodeAutoBot.app" ]; then
    echo "  BUILD SUCCESS"
    echo "  Output: dist/ClaudeCodeAutoBot.app"
    echo "  Run:    open dist/ClaudeCodeAutoBot.app"
else
    echo "  BUILD FAILED - check output above"
fi
echo "============================================"
echo
