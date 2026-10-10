# -*- mode: python ; coding: utf-8 -*-
<<<<<<< HEAD
from PyInstaller.utils.hooks import collect_all

datas = [('dist', 'dist'), ('resources', 'resources'), ('icons', 'icons'), ('tools', 'tools'), ('data', 'data')]
binaries = []
hiddenimports = ['PyQt6.sip', 'PyQt6.QtSvg', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineQuick', 'PyQt6.QtPrintSupport']
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
=======
>>>>>>> 3e4104e24bf0fa17c5d25c77d7ba1bc88d7f7a71


a = Analysis(
    ['main.py'],
    pathex=[],
<<<<<<< HEAD
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
=======
    binaries=[],
    datas=[('dist', 'dist'), ('resources', 'resources'), ('icons', 'icons'), ('tools', 'tools')],
    hiddenimports=['PyQt6.sip', 'PyQt6.QtSvg'],
>>>>>>> 3e4104e24bf0fa17c5d25c77d7ba1bc88d7f7a71
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
    name='Sales Aura',
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
    icon=['icons/sales Aura.ico'],
<<<<<<< HEAD
    contents_directory='.',
=======
>>>>>>> 3e4104e24bf0fa17c5d25c77d7ba1bc88d7f7a71
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Sales Aura',
)
