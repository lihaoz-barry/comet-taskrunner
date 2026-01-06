# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Comet Task Runner - Tray Mode

This configuration bundles the tray application into a standalone .exe file
that runs as a system tray application (no console window).

Usage:
    pyinstaller backend-tray.spec

Output:
    dist/backend-tray.exe
"""

block_cipher = None

a = Analysis(
    ['src/tray_app.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        # Include templates directory for AI automation
        ('templates', 'templates'),
        # Include config directory for window matching configuration
        ('config', 'config'),
        # Include workflows directory for YAML workflow definitions
        ('workflows', 'workflows'),
        # Include Resources directory for icon
        ('Resources', 'Resources'),
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
        'colorama',  # For ANSI color support in Windows console
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
        # Tray modules (new)
        'tray',
        'tray.tray_controller',
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
        'workflow.actions.webhook_action',
        'workflow.actions.composite_action',
        'workflow.actions.scroll_action',
        # Utility modules
        'utils',
        'utils.cleanup',
        'utils.logger',
        # Automation modules
        'automation',
        'automation.window_manager',
        'automation.ai_automator',
        'automation.pattern_matcher',
        'automation.screenshot_capture',
        'automation.mouse_controller',
        # Backend module
        'backend',
        'task_manager',
        'task_queue',
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
    name='backend-tray',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression to reduce file size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # NO console window - this is a tray app!
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Resources/comet_icon.png',  # Using PNG for now, ICO in Phase 3
)
