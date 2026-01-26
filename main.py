# main.py

import sys
import ctypes

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont

from ui.app import PasswordManagerApp


def main():
    # REQUIRED for Windows taskbar icon grouping
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "VaultX.PasswordManager"
    )

    app = QApplication(sys.argv)

    # Force a sane default font BEFORE stylesheets
    app.setFont(QFont("Segoe UI", 10))

    # Application icon (window + taskbar)
    app.setWindowIcon(QIcon("icon/content.png"))

    # Load theme
    try:
        with open("ui/theme.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    window = PasswordManagerApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
