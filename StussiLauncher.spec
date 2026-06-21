# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_all

qt_datas, qt_binaries, qt_hiddenimports = collect_all('PySide6')

# Include runtime assets used by the UI.
datas = [
    ('stussi logo sem fundo.png', '.'),
    ('somstussi.wav', '.'),
    ('icon.ico', '.'),
]
datas += collect_data_files('PySide6')
datas += qt_datas

binaries = qt_binaries
hiddenimports = qt_hiddenimports


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='StussiLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
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
    name='StussiLauncher',
)
