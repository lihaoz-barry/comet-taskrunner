"""
Tray Module for Comet Task Runner

This module provides system tray functionality for running the backend
as a background service with user-friendly controls.
"""

from .icon_tray import main, show_logs, exit_app

__all__ = ['main', 'show_logs', 'exit_app']
