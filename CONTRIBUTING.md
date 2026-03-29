# Contributing to Claude Code Auto-Bot

Thanks for your interest in contributing!

## Getting Started

1. Fork the repo
2. Clone your fork
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python claude_code_auto_bot.py
   ```

## Development

The entire app is a single Python file (`claude_code_auto_bot.py`) using Tkinter. No build step needed for development — just edit and run.

### OCR Engines

- **Windows:** Uses `winocr` (Windows built-in OCR)
- **Mac/Linux:** Uses `pytesseract` (requires Tesseract binary)

### Building Executables

- **Windows:** `build.bat` — creates `.exe` via PyInstaller
- **Mac:** `./build_mac.sh` — creates `.app` bundle via PyInstaller

## Submitting Changes

1. Create a branch for your change
2. Make your changes
3. Test on your platform (Windows/Mac/Linux)
4. Open a pull request with a clear description of what changed and why

## Reporting Bugs

Use the [bug report template](https://github.com/jasontro/claude-code-auto-bot/issues/new?template=bug_report.md) and include:
- Your OS and Python version
- Steps to reproduce
- What you expected vs. what happened

## Code Style

- Keep it simple — the project is intentionally a single file
- Follow existing patterns in the codebase
- Test on at least one platform before submitting
