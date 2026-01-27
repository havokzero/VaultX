# main.py

import sys
import ctypes

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont

from ui.app import PasswordManagerApp
from utils.resources import resource_path


def main():
    # REQUIRED for Windows taskbar icon grouping
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "VaultX.PasswordManager"
    )

    app = QApplication(sys.argv)

    # Prevent Qt font spam
    app.setFont(QFont("Segoe UI", 10))

    # Load application icon (ICO is mandatory on Windows)
    app_icon = QIcon(resource_path("icon/content.ico"))
    app.setWindowIcon(app_icon)

    # Load theme
    try:
        with open(resource_path("ui/theme.qss"), "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    window = PasswordManagerApp()
    window.setWindowIcon(app_icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
