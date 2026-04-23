# AutoBot for Claude Code — Project Context

## Project Identity
- **Name:** AutoBot for Claude Code
- **Repo:** https://github.com/jasontro/autobot-for-claude-code
- **Owner:** Jason (GitHub: jasontro, email: jasontrottier@gmail.com)
- **License:** MIT
- **Name history:** Claude Code Watcher → Claude Code Auto-Bot → AutoBot for Claude Code (renamed to avoid leading with Anthropic's trademark)

## What It Does
Single-file Python/Tkinter app that monitors a screen region using OCR and auto-approves Claude Code permission prompts by clicking + pressing a configurable key. Cross-platform: Windows, Mac, Linux.

## Key Files
- `claude_code_auto_bot.py` — entire app (~1156 lines, single file)
- `claude_code_auto_bot.spec` — Windows PyInstaller spec → `dist/ClaudeCodeAutoBot/ClaudeCodeAutoBot.exe`
- `claude_code_auto_bot_mac.spec` — Mac PyInstaller spec → `dist/ClaudeCodeAutoBot.app`
- `build.bat` — Windows build script
- `build_mac.sh` — Mac build script
- `install.py` — cross-platform dependency installer (handles Tesseract on Mac/Linux)
- `auto_bot.ico` — app icon
- `preview.png` — screenshot of the app in action (used in README + GitHub social preview)
- `rthook_errorhandler.py` — PyInstaller runtime hook, shows error dialog on crash (Windows)

## Tech Decisions
- **Windows OCR:** `winocr` (uses Windows built-in OCR, no external install)
- **Mac/Linux OCR:** `pytesseract` + Tesseract binary (installed via `install.py`)
- **Build:** PyInstaller one-folder mode (not one-file) — more reliable across machines
- **Theme persistence:** Saved to `~/.autobot_theme`
- **AppUserModelID:** `autobot.forclaudecode.v1` (Windows taskbar grouping)

## GitHub Setup (Completed)
- Public repo at https://github.com/jasontro/autobot-for-claude-code
- Description: "Auto-approves Claude Code permission prompts using OCR. Not affiliated with Anthropic."
- Topics: claude-code, auto-approve, ocr, python, tkinter, automation, developer-tools
- README has app screenshot, install instructions, usage table, build instructions
- CONTRIBUTING.md added
- Issue templates: bug report + feature request (`.github/ISSUE_TEMPLATE/`)
- `.gitignore` excludes: `build/`, `dist/`, `.claude/`, `__pycache__/`, `*.pyc`, `.DS_Store`

## Outstanding Tasks
- [ ] **GitHub Release** — rebuild exe, zip `dist/ClaudeCodeAutoBot/`, create v1.0.0 release
- [ ] **Social preview image** — upload `preview.png` manually at: GitHub repo Settings → Social preview
- [ ] **Mac build** — must be done on Mac: `./build_mac.sh` → upload `.app` zip to GitHub Release
- [ ] **GitHub username rename** — Jason considering renaming `jasontro`. Do BEFORE sharing publicly or all links break.

## How to Build (Windows)
PyInstaller is not on system PATH — use this instead:
```
python -m PyInstaller claude_code_auto_bot.spec --noconfirm
```
**Important:** Close any running `ClaudeCodeAutoBot.exe` first — if it's open, `dist/` will be locked and the build fails with PermissionError.

## How to Create the GitHub Release
```powershell
# 1. Build the exe first (see above)
# 2. Zip the output folder
cd "X:\Jason\App Development\Claude Watcher\Claude Watcher v3\dist"
Compress-Archive -Path ClaudeCodeAutoBot -DestinationPath ClaudeCodeAutoBot-Windows-v1.0.0.zip

# 3. Create the release
gh release create v1.0.0 ClaudeCodeAutoBot-Windows-v1.0.0.zip `
  --title "v1.0.0 — AutoBot for Claude Code" `
  --notes "Initial release. Windows .exe included. Mac/Linux: run from source or build with build_mac.sh."
```

## Running from Source
```bash
pip install -r requirements.txt
python claude_code_auto_bot.py
```
