# ui/app.py

import hmac
import hashlib

from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QApplication,
    QMessageBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer, QEvent

from ui.login import LoginView
from ui.vault_view import VaultView
from storage.vault import VaultStorage
from crypto.kdf import generate_salt, derive_key
from utils.hotkey import GlobalHotkey

from config import (
    TITLE_TEXT,
    TITLE_SCROLL_SPEED_MS,
    AUTO_LOCK_MINUTES,
    LOCK_ON_BLUR,
)


class PasswordManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # ------------------------
        # Window basics
        # ------------------------

        self.setWindowIcon(QIcon("icon/content.png"))
        self.resize(900, 600)

        # ------------------------
        # Core state
        # ------------------------

        self.storage = VaultStorage()
        self.master_key: bytes | None = None

        self.base_title = TITLE_TEXT
        self.scroll_index = 0

        # ------------------------
        # UI stack
        # ------------------------

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.login_view = LoginView(self.login)
        self.stack.addWidget(self.login_view)

        # ------------------------
        # Init helpers
        # ------------------------

        self._init_title_scroll()
        self._init_idle_lock()
        self._init_hotkey()

    # ==========================================================
    # Initialization helpers
    # ==========================================================

    def _init_title_scroll(self):
        self.title_timer = QTimer(self)
        self.title_timer.timeout.connect(self.scroll_title)
        self.title_timer.start(TITLE_SCROLL_SPEED_MS)

    def _init_idle_lock(self):
        self.idle_timer = QTimer(self)
        self.idle_timer.setSingleShot(True)
        self.idle_timer.timeout.connect(self.lock)

        self.reset_idle_timer()
        self.installEventFilter(self)

    def _init_hotkey(self):
        # NOTE: Should be toggleable in Settings later
        self.hotkey = GlobalHotkey(self.show_launcher)
        self.hotkey.start()

    # ==========================================================
    # Window behavior
    # ==========================================================

    def scroll_title(self):
        t = self.base_title
        self.scroll_index = (self.scroll_index + 1) % len(t)
        self.setWindowTitle(t[self.scroll_index:] + t[:self.scroll_index])

    def show_launcher(self):
        self.show()
        self.raise_()
        self.activateWindow()

        if hasattr(self, "vault_view"):
            self.stack.setCurrentWidget(self.vault_view)
            self.vault_view.search.setFocus()

    # ==========================================================
    # Auto-lock logic
    # ==========================================================

    def reset_idle_timer(self):
        self.idle_timer.start(AUTO_LOCK_MINUTES * 60 * 1000)

    def eventFilter(self, obj, event):
        if event.type() in (
            QEvent.Type.MouseMove,
            QEvent.Type.KeyPress,
        ):
            self.reset_idle_timer()

        return super().eventFilter(obj, event)

    def changeEvent(self, event):
        if (
            LOCK_ON_BLUR
            and event.type() == QEvent.Type.ActivationChange
            and not self.isActiveWindow()
        ):
            self.lock()

        super().changeEvent(event)

    # ==========================================================
    # Vault lifecycle
    # ==========================================================

    def login(self, username: str, password: str):
        try:
            # ------------------------
            # First run: create account
            # ------------------------

            if not self.storage.has_account():
                salt = generate_salt()
                key = derive_key(password, salt)

                username_hash = hmac.new(
                    key,
                    username.encode("utf-8"),
                    hashlib.sha256,
                ).digest()

                verifier = hmac.new(
                    key,
                    b"vaultx-check",
                    hashlib.sha256,
                ).digest()

                self.storage.create_account(
                    username_hash=username_hash,
                    salt=salt,
                    verifier=verifier,
                )

                self.master_key = key

            # ------------------------
            # Normal login
            # ------------------------

            else:
                stored_username_hash, salt, stored_verifier = (
                    self.storage.get_account()
                )

                key = derive_key(password, salt)

                calc_username_hash = hmac.new(
                    key,
                    username.encode("utf-8"),
                    hashlib.sha256,
                ).digest()

                calc_verifier = hmac.new(
                    key,
                    b"vaultx-check",
                    hashlib.sha256,
                ).digest()

                if not (
                    hmac.compare_digest(calc_username_hash, stored_username_hash)
                    and hmac.compare_digest(calc_verifier, stored_verifier)
                ):
                    QMessageBox.warning(
                        self,
                        "Invalid login",
                        "Invalid username or master password",
                    )
                    return

                self.master_key = key

            # ------------------------
            # Open vault
            # ------------------------

            self.vault_view = VaultView(
                self.storage,
                lambda: self.master_key,
                self.lock,
            )

            self.stack.addWidget(self.vault_view)
            self.stack.setCurrentWidget(self.vault_view)

            self.reset_idle_timer()

        except Exception:
            QMessageBox.critical(self, "Error", "Failed to unlock vault")
            self.master_key = None

    def lock(self):
        """
        Hard lock:
        - Drop master key
        - Clear clipboard
        - Return to login view
        """

        self.master_key = None

        try:
            clipboard = QApplication.clipboard()
            clipboard.clear()
        except Exception:
            pass

        self.stack.setCurrentWidget(self.login_view)
