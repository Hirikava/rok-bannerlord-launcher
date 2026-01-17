# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = "./dist"
# Specify the binaries in the spec file
binaries = collect_dynamic_libs('glfw')

rok_launcher_a = Analysis(
    ['./start.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(rok_launcher_a.pure)

rok_launcher_exe = EXE(
    pyz,
    rok_launcher_a.scripts,
    [],
    exclude_binaries=True,
    name='rok_bannerlord_launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    windowed=True,
)


coll = COLLECT(
    rok_launcher_exe,
    rok_launcher_a.binaries,
    rok_launcher_a.datas,

    upx_exclude=[],
    name='rok_bannerlord_launcher'
)
