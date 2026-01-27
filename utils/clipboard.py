# utils/clipboard.py

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

_clipboard_timer: QTimer | None = None


def copy_with_timeout(text: str, seconds: int = 15):
    global _clipboard_timer

    clipboard = QApplication.clipboard()
    clipboard.setText(text)

    # Kill any existing timer
    if _clipboard_timer:
        _clipboard_timer.stop()
        _clipboard_timer.deleteLater()

    _clipboard_timer = QTimer(QApplication.instance())
    _clipboard_timer.setSingleShot(True)
    _clipboard_timer.timeout.connect(clipboard.clear)
    _clipboard_timer.start(seconds * 1000)
