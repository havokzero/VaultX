# ui/vault_view.py

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QTabWidget,
    QGroupBox,
)

import time

from models.entry import VaultEntry
from crypto.cipher import encrypt, decrypt
from utils.clipboard import copy_with_timeout
from utils.password_gen import generate_password, password_strength
from ui.settings_view import SettingsView
from ui.change_master_dialog import ChangeMasterPasswordDialog



class VaultView(QWidget):
    def __init__(self, storage, get_key, lock_callback):
        super().__init__()

        self.storage = storage
        self.get_key = get_key
        self.lock_callback = lock_callback

        self.entries = []
        self.entry_ids = []

        root = QVBoxLayout(self)

        # ======================
        # Tabs
        # ======================
        tabs = QTabWidget()
        root.addWidget(tabs)

        vault_tab = QWidget()
        settings_tab = SettingsView(self.change_master_password)

        tabs.addTab(vault_tab, "Vault")
        tabs.addTab(settings_tab, "Settings")

        vault_layout = QHBoxLayout(vault_tab)

        # ======================
        # Left: Entry list
        # ======================
        left = QVBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search vault")
        self.search.textChanged.connect(self.apply_filter)
        left.addWidget(self.search)

        self.list = QListWidget()
        self.list.itemClicked.connect(self.show_entry)
        left.addWidget(self.list)

        vault_layout.addLayout(left, 2)

        # ======================
        # Middle: Credentials
        # ======================
        middle = QVBoxLayout()

        self.site = QLineEdit()
        self.site.setPlaceholderText("Site")
        middle.addWidget(self.site)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")
        middle.addWidget(self.user)

        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("Password")
        middle.addWidget(self.pwd)

        self.strength_label = QLabel("Strength: —")
        self.strength_label.setStyleSheet("color: #6272a4; font-weight: bold;")
        middle.addWidget(self.strength_label)

        gen_btn = QPushButton("Generate Strong Password")
        gen_btn.clicked.connect(self.generate_password)
        middle.addWidget(gen_btn)

        add_btn = QPushButton("Add / Update Entry")
        add_btn.clicked.connect(self.add_or_update_entry)
        middle.addWidget(add_btn)

        copy_btn = QPushButton("Copy Password")
        copy_btn.clicked.connect(self.copy_password)
        middle.addWidget(copy_btn)

        delete_btn = QPushButton("Delete Entry")
        delete_btn.clicked.connect(self.delete_entry)
        middle.addWidget(delete_btn)

        lock_btn = QPushButton("Lock Vault")
        lock_btn.clicked.connect(self.lock_callback)
        middle.addWidget(lock_btn)

        middle.addStretch()
        vault_layout.addLayout(middle, 3)

        # ======================
        # Right: Notes
        # ======================
        notes_box = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_box)

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes for this entry")
        notes_layout.addWidget(self.notes)

        vault_layout.addWidget(notes_box, 3)

        # Signals
        self.pwd.textChanged.connect(self.update_strength)

        self.refresh()

    # ------------------------
    # Vault logic
    # ------------------------

    def refresh(self):
        self.list.clear()
        self.entries.clear()
        self.entry_ids.clear()

        key = self.get_key()
        if not key:
            return

        for entry_id, blob in self.storage.get_all_entries():
            decrypted = decrypt(key, blob)
            entry = VaultEntry.deserialize(decrypted)
            self.entries.append(entry)
            self.entry_ids.append(entry_id)

        combined = list(zip(self.entries, self.entry_ids))
        combined.sort(key=lambda x: x[0].last_used, reverse=True)

        if combined:
            self.entries, self.entry_ids = zip(*combined)
            self.entries = list(self.entries)
            self.entry_ids = list(self.entry_ids)

        for entry in self.entries:
            self.list.addItem(entry.site)

    def find_existing_index(self, site: str):
        site = site.lower()
        for i, entry in enumerate(self.entries):
            if entry.site.lower() == site:
                return i
        return None

    def add_or_update_entry(self):
        key = self.get_key()
        if not key:
            QMessageBox.warning(self, "Locked", "Vault is locked.")
            return

        if not self.site.text() or not self.pwd.text():
            QMessageBox.warning(self, "Missing data", "Site and password required.")
            return

        entry = VaultEntry(
            site=self.site.text(),
            username=self.user.text(),
            password=self.pwd.text(),
            notes=self.notes.toPlainText(),
        )

        blob = encrypt(key, entry.serialize())
        idx = self.find_existing_index(entry.site)

        if idx is not None:
            self.storage.update_entry(self.entry_ids[idx], blob)
        else:
            self.storage.add_entry(blob)

        self.refresh()
        self.clear_fields()

    def delete_entry(self):
        row = self.list.currentRow()
        if row < 0:
            return

        self.storage.delete_entry(self.entry_ids[row])
        self.refresh()
        self.clear_fields()

    def show_entry(self):
        row = self.list.currentRow()
        if row < 0:
            return

        entry = self.entries[row]

        entry.touch()  # update last_used on view

        blob = encrypt(self.get_key(), entry.serialize())
        self.storage.update_entry(self.entry_ids[row], blob)

        self.site.setText(entry.site)
        self.user.setText(entry.username)
        self.pwd.setText(entry.password)
        self.notes.setText(entry.notes)

        self.update_strength()

    def copy_password(self):
        key = self.get_key()
        if not key:
            return

        row = self.list.currentRow()
        if row < 0:
            return

        entry = self.entries[row]
        entry.last_used = time.time()

        blob = encrypt(key, entry.serialize())
        self.storage.update_entry(self.entry_ids[row], blob)

        copy_with_timeout(entry.password)
        self.refresh()

    def apply_filter(self):
        q = self.search.text().lower()
        self.list.clear()

        for entry in self.entries:
            if q in entry.site.lower() or q in entry.domain:
                self.list.addItem(entry.site)

    def clear_fields(self):
        self.site.clear()
        self.user.clear()
        self.pwd.clear()
        self.notes.clear()
        self.strength_label.setText("Strength: —")

    # ------------------------
    # Password tools
    # ------------------------

    def generate_password(self):
        pwd = generate_password(length=20)
        self.pwd.setText(pwd)
        self.update_strength()

    def update_strength(self):
        pwd = self.pwd.text()

        if not pwd:
            self.strength_label.setText("Strength: —")
            self.strength_label.setProperty("strength", "")
            self.strength_label.style().polish(self.strength_label)
            return

        strength = password_strength(pwd)
        self.strength_label.setText(f"Strength: {strength}")

        mapping = {
            "Weak": "weak",
            "Okay": "ok",
            "Strong": "strong",
            "Very Strong": "very",
        }

        self.strength_label.setProperty(
            "strength", mapping.get(strength, "")
        )
        self.strength_label.style().polish(self.strength_label)

    # ------------------------
    # Settings hooks
    # ------------------------

    def change_master_password(self):
        dlg = ChangeMasterPasswordDialog(self.storage, self.get_key)
        dlg.exec()

