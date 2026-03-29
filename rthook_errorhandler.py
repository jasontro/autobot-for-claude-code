"""Runtime hook: catch fatal errors and show a message box instead of silently dying."""
import sys

if sys.platform == 'win32':
    _original_excepthook = sys.excepthook

    def _error_dialog(exc_type, exc_value, exc_tb):
        try:
            import ctypes
            msg = f"{exc_type.__name__}: {exc_value}"
            ctypes.windll.user32.MessageBoxW(
                0, msg, "Claude Code Auto-Bot - Error", 0x10
            )
        except Exception:
            pass
        _original_excepthook(exc_type, exc_value, exc_tb)

    sys.excepthook = _error_dialog
