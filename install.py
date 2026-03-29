#!/usr/bin/env python3
"""
Claude Code Auto-Bot — Cross-platform installer
Installs Python packages and system dependencies (Tesseract on Mac/Linux).
"""

import subprocess
import sys
import platform
import shutil


def run(cmd, check=True):
    print(f"  → {' '.join(cmd)}")
    subprocess.run(cmd, check=check)


def main():
    system = platform.system()
    print()
    print("╔══════════════════════════════════════════╗")
    print("║  Claude Code Auto-Bot — Installer         ║")
    print("╚══════════════════════════════════════════╝")
    print()

    # 1. Install Python packages
    print("[1/2] Installing Python packages...")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print()

    # 2. Install Tesseract (Mac/Linux only)
    if system == "Darwin":
        print("[2/2] Installing Tesseract OCR (Mac)...")
        if shutil.which("brew"):
            if shutil.which("tesseract"):
                print("  ✓ Tesseract already installed")
            else:
                run(["brew", "install", "tesseract"])
        else:
            print("  ✖ Homebrew not found. Install it from https://brew.sh")
            print("  Then run: brew install tesseract")
            print()

    elif system == "Linux":
        print("[2/2] Installing Tesseract OCR (Linux)...")
        if shutil.which("tesseract"):
            print("  ✓ Tesseract already installed")
        elif shutil.which("apt"):
            run(["sudo", "apt", "install", "-y", "tesseract-ocr"])
        elif shutil.which("dnf"):
            run(["sudo", "dnf", "install", "-y", "tesseract"])
        elif shutil.which("pacman"):
            run(["sudo", "pacman", "-S", "--noconfirm", "tesseract"])
        else:
            print("  ✖ Could not detect package manager.")
            print("  Please install tesseract-ocr manually.")
            print()

    else:
        print("[2/2] Windows detected — no extra system packages needed.")
        print()

    # Verify
    print("─" * 44)
    print()
    ok = True
    for mod, name in [("PIL", "Pillow"), ("pyautogui", "pyautogui")]:
        try:
            __import__(mod)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✖ {name} — MISSING")
            ok = False

    if system == "Windows":
        try:
            __import__("winocr")
            print("  ✓ winocr")
        except ImportError:
            print("  ✖ winocr — MISSING")
            ok = False
    else:
        try:
            __import__("pytesseract")
            print("  ✓ pytesseract")
        except ImportError:
            print("  ✖ pytesseract — MISSING")
            ok = False
        if shutil.which("tesseract"):
            print("  ✓ tesseract binary")
        else:
            print("  ✖ tesseract binary — MISSING")
            ok = False

    print()
    if ok:
        print("  ✓ All good! Run:  python claude_code_auto_bot.py")
    else:
        print("  ✖ Some dependencies missing — check above.")
    print()


if __name__ == "__main__":
    main()
