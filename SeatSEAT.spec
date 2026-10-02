# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SeatSEAT.py'],
    pathex=[],
    binaries=[
        ( './.venv/Lib/site-packages/cbcbox/cbc_dist_avx2/bin/libCbc-0.dll', './cbcbox/cbc_dist_avx2/bin/' ),
        ( './SeatSEAT.ico', '.' )
        ],
    datas=[],
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
    [],
    exclude_binaries=True,
    name='SeatSEAT',
    icon='SeatSEAT.ico',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SeatSEAT',
)
