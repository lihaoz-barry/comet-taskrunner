# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Comet Task Runner Backend

This configuration bundles the Flask backend into a standalone .exe file
with all Python dependencies included.

Usage:
    pyinstaller backend.spec

Output:
    dist/backend.exe (~120-180MB)
"""

block_cipher = None

a = Analysis(
    ['src/backend.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include templates directory for AI automation
        ('templates', 'templates'),
        # Include config directory for window matching configuration
        ('config', 'config'),
        # Include workflows directory for YAML workflow definitions
        ('workflows', 'workflows'),
        # Include screenshots directory (create if doesn't exist)
    ],
    hiddenimports=[
        # Explicitly include modules that PyInstaller might miss
        'pywin32',
        'win32api',
        'win32con',
        'winreg',
        'flask',
        'flask.json',
        'dotenv',  # python-dotenv
        'psutil',
        'cv2',  # opencv-python
        'numpy',
        'mss',
        'pyautogui',
        'PIL',  # Pillow
        'yaml',  # PyYAML for config loading
        # Tkinter for overlay system
        'tkinter',
        'tkinter.ttk',
        '_tkinter',
        # Overlay modules
        'overlay',
        'overlay.status_overlay',
        'overlay.overlay_config',
        'overlay.keyboard_handler',
        'overlay.system_tray',
        # Keyboard module for ESC cancellation
        'keyboard',
        # pystray for system tray
        'pystray',
        'pystray._win32',
        # Task modules
        'tasks',
        'tasks.base_task',
        'tasks.url_task',
        'tasks.ai_task',
        'tasks.configurable_task',
        # Workflow modules (our custom workflow system, not the third-party package)
        'workflow',
        'workflow.workflow_config',
        'workflow.workflow_loader',
        'workflow.step_executor',
        'workflow.actions',
        'workflow.actions.base_action',
        'workflow.actions.window_action',
        'workflow.actions.click_action',
        'workflow.actions.click_and_type_action',
        'workflow.actions.detect_action',
        'workflow.actions.detect_loop_action',
        'workflow.actions.key_press_action',
        'workflow.actions.wait_action',
        'workflow.actions.completion_action',
        'workflow.actions.close_window_action',
        'workflow.actions.clipboard_action',
        'workflow.actions.screenshot_action',
        # Utility modules
        'utils',
        'utils.cleanup',
        # Automation modules
        'automation',
        'automation.window_manager',
        'automation.ai_automator',
        'automation.pattern_matcher',
        'automation.screenshot_capture',
        'automation.mouse_controller',
    ],
    hookspath=['pyinstaller_hooks'],  # Use our custom hooks to override problematic ones
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude the third-party 'workflow' package to avoid hook conflicts
        # (we have our own custom 'workflow' module in src/)
        'Alfred-Workflow',
        'workflow.background',
        'workflow.notify',
        'workflow.update',
        'workflow.web',
        'workflow.workflow',
        # Exclude unnecessary modules to reduce size
        # Note: tkinter is now INCLUDED for overlay system
        'matplotlib',
        'pandas',
        'scipy',
        'jupyter',
        'notebook',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression to reduce file size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console window for logging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add your icon file here if you have one icon='icon.ico',
)
