# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Comet Task Runner Tray Application

Builds a windowless (no console) tray application.
"""
from PyInstaller.utils.hooks import collect_submodules

# Collect submodules
hiddenimports = []
hiddenimports += collect_submodules('tasks')
hiddenimports += collect_submodules('utils')
hiddenimports += collect_submodules('overlay')
hiddenimports += collect_submodules('workflow')
hiddenimports += collect_submodules('automation')
hiddenimports += collect_submodules('tray')

a = Analysis(
    ['src/tray/icon_tray.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('Resources', 'Resources'),
        ('workflows', 'workflows'),
        ('config', 'config'),
        ('templates', 'templates'),
    ],
    hiddenimports=hiddenimports + [
        'pystray',
        'pystray._win32',
        'PIL',
        'flask',
        'dotenv',
        'colorama',
        'psutil',
        'cv2',
        'numpy',
        'mss',
        'pyautogui',
        'yaml',
        'keyboard',
        'tkinter',
        'win32api',
        'win32con',
        'winreg',
    ],
    hookspath=['pyinstaller_hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'scipy',
        'jupyter',
        'notebook',
        'IPython',
    ],
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
    name='CometTaskRunnerTray',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # NO console window - tray app!
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Resources/comet_icon.png',
)
