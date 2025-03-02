# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# 1. Определяем абсолютный путь к текущему файлу (.spec файлу)
current_file_path = Path("AbraCadabra").resolve()

project_root = current_file_path.parent
source_path = project_root / "Source"
datas = [(str(source_path), 'Source')]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HomographyMatrixCalculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
