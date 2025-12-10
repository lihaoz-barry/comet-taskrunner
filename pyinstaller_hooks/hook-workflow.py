"""
Custom hook to override the problematic workflow hook from _pyinstaller_hooks_contrib.

This prevents PyInstaller from trying to use the broken hook-workflow.py that
expects the third-party Alfred-Workflow package, which we don't use.

Our project has a custom 'workflow' module in src/workflow/ which is handled
by standard PyInstaller mechanisms.
"""

# Empty hook - no special handling needed for our custom workflow module
# PyInstaller will automatically discover and include it via normal import analysis
