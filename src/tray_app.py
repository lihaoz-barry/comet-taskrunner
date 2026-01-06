"""
Comet Task Runner - Tray Application Entry Point

This is the main entry point for running the backend as a system tray application.
Flask runs in a background thread while the tray icon is the main UI.

Usage:
    python src/tray_app.py
    
Or when packaged:
    backend-tray.exe
"""

import os
import sys
import threading
import time
import atexit
import signal

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tray import TrayController

# Import backend components
from utils.logger import setup_logging

# Setup logging first
logger = setup_logging()


class CometTrayApp:
    """Main application class for tray mode"""
    
    def __init__(self):
        self.flask_thread = None
        self.flask_app = None
        self.task_queue = None
        self.tray = None
        self.shutdown_event = threading.Event()
    
    def _start_flask(self):
        """Start Flask server in background thread"""
        try:
            # Import backend module
            import backend
            
            # Store references
            self.flask_app = backend.app
            self.task_queue = backend.task_queue
            
            # Start Flask (this blocks in this thread)
            logger.info("Flask server starting on 0.0.0.0:5000...")
            backend.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            
        except Exception as e:
            logger.error(f"Flask server error: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_show_log(self):
        """Callback when Show Log is clicked"""
        # Phase 2 will implement this
        logger.info("Show Log clicked - feature coming in Phase 2")
    
    def _on_exit(self):
        """Callback when Exit is clicked"""
        logger.info("Exit requested - shutting down...")
        self.shutdown()
    
    def _init_backend(self):
        """Initialize backend components before starting Flask"""
        import backend
        
        # Run the initialization that normally happens in __main__
        logger.info("=" * 60)
        logger.info("Starting Comet Task Runner (Tray Mode)")
        logger.info("=" * 60)
        
        # Check API Key
        api_key = os.environ.get('COMET_API_KEY')
        if not api_key:
            logger.error("COMET_API_KEY not set!")
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "错误: COMET_API_KEY 环境变量未设置!\n\n"
                    "请设置后重试:\n"
                    "set COMET_API_KEY=your-key",
                    "Comet Task Runner",
                    0x10  # MB_ICONERROR
                )
            except:
                pass
            sys.exit(1)
        
        logger.info(f"✓ API Key detected (Length: {len(api_key)})")
        
        # Initialize TaskQueue
        comet_path = backend.get_comet_path()
        if comet_path:
            backend.task_queue = backend.TaskQueue(comet_path)
            self.task_queue = backend.task_queue
            logger.info(f"✓ TaskQueue initialized")
        else:
            logger.warning("⚠ Comet browser not found")
        
        # Start task monitor
        backend.start_task_monitor()
        logger.info("✓ Task monitor started")
    
    def start(self):
        """Start the tray application"""
        logger.info("Initializing Comet Task Runner Tray App...")
        
        # Register cleanup
        atexit.register(self.cleanup)
        
        # Initialize backend
        self._init_backend()
        
        # Start Flask in background thread
        self.flask_thread = threading.Thread(target=self._start_flask, daemon=True)
        self.flask_thread.start()
        logger.info("✓ Flask server thread started")
        
        # Give Flask a moment to start
        time.sleep(1)
        
        # Create and start tray (this blocks)
        self.tray = TrayController(
            on_show_log=self._on_show_log,
            on_exit=self._on_exit
        )
        
        logger.info("✓ Starting system tray...")
        logger.info("=" * 60)
        logger.info("Comet Task Runner is running in system tray")
        logger.info("Right-click tray icon for options")
        logger.info("=" * 60)
        
        # This blocks until tray is stopped
        self.tray.start()
        
        # If we get here, tray was stopped
        self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down...")
        
        self.shutdown_event.set()
        
        # Stop tray
        if self.tray:
            self.tray.stop()
        
        # Cleanup
        self.cleanup()
        
        logger.info("Goodbye!")
        
        # Force exit (Flask thread might still be running)
        os._exit(0)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            from utils.cleanup import cleanup_temp_files
            cleanup_temp_files()
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")


def main():
    """Main entry point"""
    app = CometTrayApp()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal")
        app.shutdown()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        app.start()
    except KeyboardInterrupt:
        app.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
