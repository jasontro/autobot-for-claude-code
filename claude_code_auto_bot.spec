# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import glob
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Collect winocr and winrt dynamic libraries and data files
extra_datas = []
extra_binaries = []

# Explicitly bundle VC++ runtime DLLs so the exe works on machines without them
python_dir = os.path.dirname(sys.executable)
for pattern in ['vcruntime*.dll', 'msvcp*.dll', 'concrt*.dll', 'vcomp*.dll']:
    for dll in glob.glob(os.path.join(python_dir, pattern)):
        extra_binaries.append((dll, '.'))

for pkg in [
    'winocr',
    'winrt_runtime',
    'winrt_windows_foundation',
    'winrt_windows_foundation_collections',
    'winrt_windows_globalization',
    'winrt_windows_graphics_imaging',
    'winrt_windows_media_ocr',
    'winrt_windows_storage_streams',
]:
    try:
        extra_datas += collect_data_files(pkg)
    except Exception:
        pass
    try:
        extra_binaries += collect_dynamic_libs(pkg)
    except Exception:
        pass

a = Analysis(
    ['claude_code_auto_bot.py'],
    pathex=[],
    binaries=extra_binaries,
    datas=extra_datas + [('auto_bot.ico', '.')],
    hiddenimports=[
        # Core app deps
        'PIL',
        'PIL.ImageGrab',
        'PIL.Image',
        'pyautogui',
        'winsound',
        'asyncio',
        'colorsys',
        # winocr
        'winocr',
        # winrt runtime and submodules (v3.x package naming)
        'winrt.runtime',
        'winrt.system',
        'winrt.windows.foundation',
        'winrt.windows.foundation.collections',
        'winrt.windows.globalization',
        'winrt.windows.graphics.imaging',
        'winrt.windows.media.ocr',
        'winrt.windows.storage.streams',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rthook_errorhandler.py'],
    excludes=[
        'pytesseract',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# One-folder mode: more reliable across machines
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
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='auto_bot.ico',
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
