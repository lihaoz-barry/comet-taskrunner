"""
Automation Module - Window Management

Handles window detection, activation, and management for Comet browser.
Implements multi-layer validation strategy for precise window matching.
"""

import time
import ctypes
import logging
import winreg
import yaml
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
import win32gui
import win32process
import win32con
import win32api

logger = logging.getLogger(__name__)


class WindowManager:
    """
    Window detection and activation for Comet browser.

    Features:
    - Multi-layer validation (6 layers)
    - Window class name matching (most reliable)
    - Process name and path verification
    - Scoring system for best match selection
    - Configuration-driven matching strategy
    - Multi-monitor support
    """

    def __init__(self, config_path: str = None):
        """
        Initialize WindowManager with configuration.

        Args:
            config_path: Path to window_matching.yaml (default: config/window_matching.yaml)
        """
        if config_path is None:
            # Default config path
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "window_matching.yaml"

        self.config = self._load_config(config_path)
        logger.info("WindowManager initialized with config-driven matching strategy")

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        try:
            if not Path(config_path).exists():
                logger.warning(f"Config file not found: {config_path}, using defaults")
                return self._get_default_config()

            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = yaml.safe_load(f)
                config = full_config.get('comet_browser', {})
                logger.info(f"Loaded configuration from {config_path}")
                return config

        except Exception as e:
            logger.error(f"Failed to load config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'window_class': 'Chrome_WidgetWin_1',
            'process_name': 'comet.exe',
            'process_path_contains': 'comet.exe',
            'title_keywords': ['Comet', 'Perplexity'],
            'exclude_keywords': ['TaskRunner Monitor', 'AI TASK MONITOR', 'python.exe',
                                'cmd.exe', 'powershell.exe', 'backend.exe'],
            'min_width': 400,
            'min_height': 300,
            'validation': {
                'require_class_match': True,
                'require_process_match': True,
                'require_process_path_match': True,
                'require_title_keyword': False
            },
            'scoring': {
                'base_score': 100,
                'keyword_bonus': 20,
                'large_width_bonus': 10,
                'large_height_bonus': 10,
                'position_bonus': 5
            },
            'debug': {
                'log_all_candidates': False,
                'log_rejection_reasons': True,
                'verbose': False
            }
        }

    def find_comet_window(self) -> Optional[Tuple[int, Tuple[int, int, int, int]]]:
        """
        Find Comet browser window using multi-layer validation.

        Validation layers (in order):
        1. Basic visibility and window hierarchy checks
        2. Window style filtering (exclude tool windows)
        3. Window class name matching (CORE - most reliable)
        4. Process name verification
        5. Process path verification (NEW - ensures process contains "comet.exe")
        6. Title keyword matching and exclusion
        7. Window size validation

        Scoring system:
        - Multiple candidates are scored based on various criteria
        - Best match is selected based on highest score

        Returns:
            Tuple of (hwnd, rect) or None if not found
        """
        if self.config.get('debug', {}).get('verbose', False):
            logger.info("=" * 60)
            logger.info("WINDOW MATCHING - MULTI-LAYER VALIDATION")
            logger.info("=" * 60)

        candidates = []

        def enum_callback(hwnd, _):
            """Callback for EnumWindows - validates each window"""
            rejection_reason = self._validate_window(hwnd)

            if rejection_reason is None:
                # Window passed all validations - add as candidate
                try:
                    title = win32gui.GetWindowText(hwnd)
                    rect = win32gui.GetWindowRect(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)

                    # Calculate score
                    score = self._calculate_score(hwnd, title, rect)

                    candidate = {
                        'hwnd': hwnd,
                        'title': title,
                        'class': class_name,
                        'rect': rect,
                        'pid': pid,
                        'score': score
                    }

                    candidates.append(candidate)

                    if self.config.get('debug', {}).get('log_all_candidates', False):
                        logger.info(f"✓ CANDIDATE: '{title}' (score: {score})")

                except Exception as e:
                    logger.warning(f"Error processing candidate window {hwnd}: {e}")

            elif self.config.get('debug', {}).get('log_rejection_reasons', False):
                try:
                    title = win32gui.GetWindowText(hwnd) or "(No Title)"
                    logger.debug(f"✗ REJECTED: '{title}' - {rejection_reason}")
                except:
                    pass

            return True  # Continue enumeration

        # Enumerate all windows
        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception as e:
            logger.error(f"Window enumeration failed: {e}")
            return None

        # Process results
        if not candidates:
            logger.warning("No matching Comet window found (all windows rejected)")
            return None

        # Select best match (highest score)
        best_match = max(candidates, key=lambda x: x['score'])

        logger.info(f"✓ MATCHED: '{best_match['title']}'")
        logger.info(f"  Class: {best_match['class']}")
        logger.info(f"  PID: {best_match['pid']}")
        logger.info(f"  Score: {best_match['score']}")
        logger.info(f"  HWND: {best_match['hwnd']}")

        if len(candidates) > 1:
            logger.info(f"  (Selected best match from {len(candidates)} candidates)")

        return (best_match['hwnd'], best_match['rect'])

    def _validate_window(self, hwnd: int) -> Optional[str]:
        """
        Multi-layer window validation.

        Args:
            hwnd: Window handle

        Returns:
            None if valid, rejection reason string if invalid
        """
        # ======================================================================
        # LAYER 1: Basic Visibility and Hierarchy
        # ======================================================================

        if not win32gui.IsWindowVisible(hwnd):
            return "not visible"

        if win32gui.IsIconic(hwnd):
            return "minimized"

        # Exclude child windows
        if win32gui.GetParent(hwnd) != 0:
            return "child window"

        # ======================================================================
        # LAYER 2: Window Style Filtering
        # ======================================================================

        try:
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            # Exclude tool windows (like our overlay)
            if ex_style & win32con.WS_EX_TOOLWINDOW:
                return "tool window (WS_EX_TOOLWINDOW)"
        except Exception as e:
            logger.debug(f"Could not get window style for HWND {hwnd}: {e}")

        # ======================================================================
        # LAYER 3: Window Class Name (CORE VALIDATION)
        # ======================================================================

        if self.config.get('validation', {}).get('require_class_match', True):
            try:
                class_name = win32gui.GetClassName(hwnd)
                expected_class = self.config.get('window_class', '')

                if class_name != expected_class:
                    return f"class mismatch (got '{class_name}', expected '{expected_class}')"
            except Exception as e:
                return f"cannot get class name: {e}"

        # ======================================================================
        # LAYER 4: Process Name Verification
        # ======================================================================

        if self.config.get('validation', {}).get('require_process_match', True):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc_name = self._get_process_name(pid)
                expected_proc = self.config.get('process_name', '')

                if not proc_name:
                    return "cannot get process name"

                if proc_name.lower() != expected_proc.lower():
                    return f"process mismatch (got '{proc_name}', expected '{expected_proc}')"
            except Exception as e:
                return f"process verification failed: {e}"

        # ======================================================================
        # LAYER 5: Process Path Verification (NEW - User Requested)
        # ======================================================================

        if self.config.get('validation', {}).get('require_process_path_match', True):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc_path = self._get_process_path(pid)
                expected_substring = self.config.get('process_path_contains', '')

                if not proc_path:
                    return "cannot get process path"

                # Case-insensitive path matching
                if expected_substring.lower() not in proc_path.lower():
                    return f"process path mismatch (path '{proc_path}' does not contain '{expected_substring}')"
            except Exception as e:
                return f"process path verification failed: {e}"

        # ======================================================================
        # LAYER 6: Title Keyword Matching
        # ======================================================================

        try:
            title = win32gui.GetWindowText(hwnd).lower()
        except:
            title = ""

        # Check exclusion list
        exclude_keywords = self.config.get('exclude_keywords', [])
        for keyword in exclude_keywords:
            if keyword.lower() in title:
                return f"excluded keyword '{keyword}' found in title"

        # Check required keywords (optional)
        if self.config.get('validation', {}).get('require_title_keyword', False):
            title_keywords = self.config.get('title_keywords', [])
            has_keyword = any(kw.lower() in title for kw in title_keywords)

            if not has_keyword:
                return f"no required keyword found in title"

        # ======================================================================
        # LAYER 7: Window Size Validation
        # ======================================================================

        try:
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            min_width = self.config.get('min_width', 400)
            min_height = self.config.get('min_height', 300)

            if width < min_width or height < min_height:
                return f"too small ({width}x{height}, minimum {min_width}x{min_height})"
        except Exception as e:
            return f"cannot get window size: {e}"

        # ======================================================================
        # All validations passed!
        # ======================================================================

        return None

    def _calculate_score(self, hwnd: int, title: str, rect: Tuple[int, int, int, int]) -> int:
        """
        Calculate window match score for ranking candidates.

        Args:
            hwnd: Window handle
            title: Window title
            rect: Window rectangle (left, top, right, bottom)

        Returns:
            Score (higher is better)
        """
        scoring_config = self.config.get('scoring', {})

        score = scoring_config.get('base_score', 100)

        # Title keyword bonus
        title_lower = title.lower()
        title_keywords = self.config.get('title_keywords', [])
        for keyword in title_keywords:
            if keyword.lower() in title_lower:
                score += scoring_config.get('keyword_bonus', 20)

        # Window size bonuses
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]

        if width > 1000:
            score += scoring_config.get('large_width_bonus', 10)

        if height > 600:
            score += scoring_config.get('large_height_bonus', 10)

        # Position bonus (not at screen edge)
        if rect[0] > 0 and rect[1] > 0:
            score += scoring_config.get('position_bonus', 5)

        return score

    @staticmethod
    def _get_process_name(pid: int) -> Optional[str]:
        """
        Get process executable name from PID.

        Args:
            pid: Process ID

        Returns:
            Process name (e.g., "Comet.exe") or None
        """
        try:
            # Try psutil first (cleaner API)
            try:
                import psutil
                return psutil.Process(pid).name()
            except ImportError:
                pass

            # Fallback to pywin32
            handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                False,
                pid
            )
            try:
                path = win32process.GetModuleFileNameEx(handle, 0)
                return Path(path).name
            finally:
                win32api.CloseHandle(handle)

        except Exception as e:
            logger.debug(f"Could not get process name for PID {pid}: {e}")
            return None

    @staticmethod
    def _get_process_path(pid: int) -> Optional[str]:
        """
        Get full process executable path from PID.

        Args:
            pid: Process ID

        Returns:
            Full path (e.g., "C:\\Program Files\\Comet\\Comet.exe") or None
        """
        try:
            # Try psutil first (cleaner API)
            try:
                import psutil
                return psutil.Process(pid).exe()
            except ImportError:
                pass

            # Fallback to pywin32
            handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                False,
                pid
            )
            try:
                path = win32process.GetModuleFileNameEx(handle, 0)
                return path
            finally:
                win32api.CloseHandle(handle)

        except Exception as e:
            logger.debug(f"Could not get process path for PID {pid}: {e}")
            return None

    # =========================================================================
    # Legacy Methods (Backward Compatibility)
    # =========================================================================

    @staticmethod
    def find_comet_window(
        keywords: list = None,
        exclude_title: str = None,
        require_process: str = None
    ) -> Optional[Tuple[int, Tuple[int, int, int, int]]]:
        """
        Static method for backward compatibility with old code.

        DEPRECATED: This method delegates to find_comet_window_legacy().
        New code should create a WindowManager() instance and call .find_comet_window()

        Args:
            keywords: List of keywords to search
            exclude_title: Optional string, skip window if title contains this
            require_process: Optional string, exact process name

        Returns:
            Tuple of (hwnd, rect) or None if not found
        """
        return WindowManager.find_comet_window_legacy(keywords, exclude_title, require_process)

    @staticmethod
    def find_comet_window_legacy(
        keywords: list = None,
        exclude_title: str = None,
        require_process: str = None
    ) -> Optional[Tuple[int, Tuple[int, int, int, int]]]:
        """
        Legacy window finding method (backward compatibility).

        DEPRECATED: Use WindowManager().find_comet_window() instead.
        This method uses the old title-based matching strategy.

        Args:
            keywords: List of keywords to search
            exclude_title: Optional string, skip window if title contains this
            require_process: Optional string, exact process name

        Returns:
            Tuple of (hwnd, rect) or None if not found
        """
        logger.warning("Using legacy window matching method (deprecated)")

        if keywords is None:
            keywords = ["Comet", "Perplexity"]

        exclude_keywords = [
            "backend.exe", "python.exe", "cmd.exe", "powershell.exe", ".py",
            "comet-taskrunner", "Antigravity", "Visual Studio Code",
            "TaskRunner Monitor", "AI TASK MONITOR"  # Exclude our overlay
        ]

        if exclude_title:
            exclude_keywords.append(exclude_title)

        found_windows = []

        def enum_callback(hwnd, _):
            if not WindowManager._is_candidate_window(hwnd):
                return True

            try:
                title = win32gui.GetWindowText(hwnd).lower()

                # Check exclusion list
                if any(ex.lower() in title for ex in exclude_keywords):
                    return True

                # Check keywords
                if any(keyword.lower() in title for keyword in keywords):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)

                    # Check process name if required
                    if require_process:
                        proc_name = WindowManager._get_process_name(pid)
                        if not proc_name or proc_name.lower() != require_process.lower():
                            return True

                    rect = win32gui.GetWindowRect(hwnd)
                    found_windows.append({
                        'hwnd': hwnd,
                        'title': win32gui.GetWindowText(hwnd),
                        'rect': rect,
                        'pid': pid
                    })
            except Exception:
                pass

            return True

        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception as e:
            logger.error(f"Window enumeration failed: {e}")
            return None

        if not found_windows:
            logger.warning(f"No match found for keywords={keywords}, process={require_process}")
            return None

        window = found_windows[0]
        logger.info(f"Found window: HWND={window['hwnd']}, Title='{window['title']}', PID={window['pid']}")

        return (window['hwnd'], window['rect'])

    # =========================================================================
    # Window Activation Methods (Unchanged)
    # =========================================================================

    @staticmethod
    def activate_window(hwnd: int) -> bool:
        """
        Forcefully activate a window and bring it to foreground.

        Uses multiple techniques to bypass Windows foreground lock:
        1. ALT key simulation
        2. AttachThreadInput
        3. Combined aggressive approach

        Args:
            hwnd: Window handle

        Returns:
            True if successful
        """
        logger.info(f"Forcefully activating window HWND={hwnd}")

        try:
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                logger.info("Window is minimized, restoring...")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)

            # Method 1: ALT key (most reliable)
            logger.debug("Trying ALT key method...")
            try:
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                time.sleep(0.05)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

                time.sleep(0.1)
                if win32gui.GetForegroundWindow() == hwnd:
                    window_title = win32gui.GetWindowText(hwnd)
                    logger.info(f"Window activated (ALT method): '{window_title}'")
                    return True
            except Exception as e:
                logger.warning(f"ALT method failed: {e}")

            # Method 2: Thread attachment
            logger.debug("Trying thread attachment method...")
            try:
                foreground_hwnd = win32gui.GetForegroundWindow()
                if foreground_hwnd:
                    foreground_tid = win32process.GetWindowThreadProcessId(foreground_hwnd)[0]
                    target_tid = win32process.GetWindowThreadProcessId(hwnd)[0]

                    ctypes.windll.user32.AttachThreadInput(target_tid, foreground_tid, True)
                    win32gui.BringWindowToTop(hwnd)
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    win32gui.SetForegroundWindow(hwnd)
                    ctypes.windll.user32.AttachThreadInput(target_tid, foreground_tid, False)

                    time.sleep(0.1)
                    if win32gui.GetForegroundWindow() == hwnd:
                        window_title = win32gui.GetWindowText(hwnd)
                        logger.info(f"Window activated (thread method): '{window_title}'")
                        return True
            except Exception as e:
                logger.warning(f"Thread method failed: {e}")

            # Method 3: Combined aggressive
            logger.debug("Trying combined method...")
            try:
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetFocus(hwnd)
                win32gui.SetForegroundWindow(hwnd)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

                time.sleep(0.15)
                if win32gui.GetForegroundWindow() == hwnd:
                    window_title = win32gui.GetWindowText(hwnd)
                    logger.info(f"Window activated (combined method): '{window_title}'")
                    return True
            except Exception as e:
                logger.warning(f"Combined method failed: {e}")

            # All methods failed
            logger.error("All activation methods failed")
            try:
                win32gui.FlashWindow(hwnd, True)
                logger.info("Flashing window to notify user")
            except:
                pass

            return False

        except Exception as e:
            logger.error(f"Complete failure to activate window: {e}")
            return False

    @staticmethod
    def close_window(hwnd: int) -> bool:
        """
        Close a window using WM_CLOSE message.

        Args:
            hwnd: Window handle

        Returns:
            True if message sent successfully
        """
        try:
            logger.info(f"Closing window HWND={hwnd}")
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to close window: {e}")
            return False

    @staticmethod
    def get_application_path(registry_subkey: str, fallback_path: str) -> Optional[str]:
        """
        Find application executable path via registry or fallback.

        Args:
            registry_subkey: Registry path
            fallback_path: Fallback file path

        Returns:
            Path to executable or None
        """
        logger.info("Searching for application path...")

        # Try registry
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, registry_subkey),
            (winreg.HKEY_LOCAL_MACHINE, registry_subkey)
        ]

        for hkey, subkey in registry_paths:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    path, _ = winreg.QueryValueEx(key, "")
                    if path and Path(path).exists():
                        logger.info(f"Found in registry: {path}")
                        return path
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.warning(f"Registry error: {e}")

        # Try fallback
        if fallback_path and Path(fallback_path).exists():
            logger.info(f"Found at fallback location: {fallback_path}")
            return fallback_path

        logger.error("Application not found in registry or fallback location")
        return None

    @staticmethod
    def _is_candidate_window(hwnd: int) -> bool:
        """
        Check if a window is a candidate (visible, not minimized, non-zero size).

        Allows negative coordinates for multi-monitor setups.
        """
        if not win32gui.IsWindowVisible(hwnd):
            return False

        if win32gui.IsIconic(hwnd):
            return False

        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            if width <= 0 or height <= 0:
                return False
        except Exception:
            return False

        return True
