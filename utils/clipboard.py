# utils/clipboard.py

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

def copy_with_timeout(text: str, seconds: int = 15):
    clipboard = QApplication.clipboard()
    clipboard.setText(text)

    #timer = QTimer(app)
    timer = QTimer(QApplication.instance())
    timer.setSingleShot(True)
    timer.timeout.connect(clipboard.clear)
    timer.start(seconds * 1000)
