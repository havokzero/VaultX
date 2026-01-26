# storage/vault.py

import sqlite3
from pathlib import Path

VAULT_PATH = Path.home() / ".vaultx"
DB_FILE = VAULT_PATH / "vault.db"


class VaultStorage:
    def __init__(self):
        VAULT_PATH.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(DB_FILE)
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()

        # Single local account (hashed username + salt + verifier)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS account (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                username_hash BLOB NOT NULL,
                salt BLOB NOT NULL,
                verifier BLOB NOT NULL
            )
        """)

        # Encrypted vault entries
        cur.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                blob BLOB NOT NULL
            )
        """)

        self.conn.commit()

    # ========================
    # Account management
    # ========================

    def has_account(self) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM account")
        return cur.fetchone()[0] > 0

    def create_account(self, username_hash: bytes, salt: bytes, verifier: bytes):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO account (id, username_hash, salt, verifier)
            VALUES (1, ?, ?, ?)
            """,
            (username_hash, salt, verifier),
        )
        self.conn.commit()

    def get_account(self):
        """
        Returns (username_hash, salt, verifier) or None
        """
        cur = self.conn.cursor()
        cur.execute(
            "SELECT username_hash, salt, verifier FROM account WHERE id = 1"
        )
        return cur.fetchone()

    def update_account(
        self,
        username_hash: bytes,
        salt: bytes,
        verifier: bytes,
    ):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE account
            SET username_hash = ?, salt = ?, verifier = ?
            WHERE id = 1
            """,
            (username_hash, salt, verifier),
        )
        self.conn.commit()

    # ========================
    # Crypto helpers (internal)
    # ========================

    def encrypt_blob(self, plaintext: bytes, key: bytes) -> bytes:
        from crypto.cipher import encrypt
        return encrypt(key, plaintext)

    def decrypt_blob(self, blob: bytes, key: bytes) -> bytes:
        from crypto.cipher import decrypt
        return decrypt(key, blob)

    # ========================
    # Vault entries
    # ========================

    def add_entry(self, blob: bytes):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO entries (blob) VALUES (?)",
            (blob,),
        )
        self.conn.commit()

    def get_all_entries(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, blob FROM entries"
        )
        return cur.fetchall()

    def update_entry(self, entry_id: int, blob: bytes):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE entries SET blob = ? WHERE id = ?",
            (blob, entry_id),
        )
        self.conn.commit()

    def delete_entry(self, entry_id: int):
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM entries WHERE id = ?",
            (entry_id,),
        )
        self.conn.commit()
