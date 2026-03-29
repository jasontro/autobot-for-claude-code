# -*- mode: python ; coding: utf-8 -*-
# macOS build spec for Claude Code Auto-Bot

block_cipher = None

a = Analysis(
    ['claude_code_auto_bot.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL',
        'PIL.ImageGrab',
        'PIL.Image',
        'pyautogui',
        'pytesseract',
        'asyncio',
        'colorsys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'winocr',
        'winsound',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ClaudeCodeAutoBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ClaudeCodeAutoBot',
)

app = BUNDLE(
    coll,
    name='ClaudeCodeAutoBot.app',
    bundle_identifier='com.claudeautobot.app',
)
