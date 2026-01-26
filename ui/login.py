# ui/login.py

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt


class LoginView(QWidget):
    """
    Login / Account creation view.

    This view is intentionally dumb:
    - It collects username + password
    - It delegates ALL logic to the app
    """

    def __init__(self, login_callback):
        super().__init__()
        self.login_callback = login_callback

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignCenter)

        # ------------------------
        # Title
        # ------------------------

        title = QLabel("VaultX")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 30px; font-weight: bold; color: #f8f8f2;"
        )
        layout.addWidget(title)

        subtitle = QLabel("Secure Local Password Vault")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6272a4;")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # ------------------------
        # Username
        # ------------------------

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setClearButtonEnabled(True)
        layout.addWidget(self.username)

        # ------------------------
        # Password
        # ------------------------

        self.password = QLineEdit()
        self.password.setPlaceholderText("Master Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setClearButtonEnabled(True)
        layout.addWidget(self.password)

        # ------------------------
        # Unlock button
        # ------------------------

        self.login_btn = QPushButton("Unlock Vault")
        self.login_btn.setDefault(True)
        self.login_btn.clicked.connect(self.submit)
        layout.addWidget(self.login_btn)

        # Enter key support
        self.username.returnPressed.connect(self.submit)
        self.password.returnPressed.connect(self.submit)

        layout.addStretch()

    # ------------------------
    # Submit
    # ------------------------

    def submit(self):
        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter both username and master password.",
            )
            return

        # Clear password field immediately (defensive UX)
        self.password.clear()

        # Delegate to application
        self.login_callback(username, password)

    # ------------------------
    # Optional helpers
    # ------------------------

    def clear(self):
        self.username.clear()
        self.password.clear()
