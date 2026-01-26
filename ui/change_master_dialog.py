# ui/change_master_dialog.py


import hmac
import hashlib

from crypto.kdf import derive_key, generate_salt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QInputDialog,
)


class ChangeMasterPasswordDialog(QDialog):
    def __init__(self, storage, get_key):
        super().__init__()
        self.storage = storage
        self.get_key = get_key

        self.setWindowTitle("Change Master Password")
        self.setModal(True)
        self.resize(400, 260)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Current Master Password"))
        self.current = QLineEdit()
        self.current.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.current)

        layout.addWidget(QLabel("New Master Password"))
        self.new = QLineEdit()
        self.new.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new)

        layout.addWidget(QLabel("Confirm New Master Password"))
        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm)

        btn = QPushButton("Change Password")
        btn.clicked.connect(self.apply)
        layout.addWidget(btn)

    def apply(self):
        if self.new.text() != self.confirm.text():
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        account = self.storage.get_account()
        if not account:
            QMessageBox.critical(self, "Error", "No account found.")
            return

        stored_username_hash, salt, verifier = account

        # Verify current password
        old_key = derive_key(self.current.text(), salt)
        check = hmac.new(old_key, b"vaultx-check", hashlib.sha256).digest()

        if not hmac.compare_digest(check, verifier):
            QMessageBox.warning(self, "Error", "Current password is incorrect.")
            return

        # Ask user for username again (required for re-hash)
        username, ok = QInputDialog.getText(
            self,
            "Confirm Username",
            "Re-enter your username to confirm password change:",
            QLineEdit.Normal,
        )

        if not ok or not username.strip():
            return

        # Derive new key
        new_salt = generate_salt()
        new_key = derive_key(self.new.text(), new_salt)

        # Re-hash username with NEW key
        new_username_hash = hmac.new(
            new_key,
            username.strip().encode("utf-8"),
            hashlib.sha256,
        ).digest()

        new_verifier = hmac.new(
            new_key,
            b"vaultx-check",
            hashlib.sha256,
        ).digest()

        # Re-encrypt entries
        entries = self.storage.get_all_entries()
        updated = []

        for entry_id, blob in entries:
            plaintext = self.storage.decrypt_blob(blob, old_key)
            new_blob = self.storage.encrypt_blob(plaintext, new_key)
            updated.append((entry_id, new_blob))

        # Commit account update
        self.storage.update_account(
            username_hash=new_username_hash,
            salt=new_salt,
            verifier=new_verifier,
        )

        for entry_id, blob in updated:
            self.storage.update_entry(entry_id, blob)

        QMessageBox.information(self, "Success", "Master password changed.")
        self.accept()
