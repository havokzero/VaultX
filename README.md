# 🔐 VaultX

**VaultX** is a local-first, offline password manager built with Python and PySide6.

No cloud.  
No sync.  
No telemetry.  
No accounts.

If you want a clean, fast, encrypted vault that lives entirely on **your** machine, this is it.

---

## ✨ Features

- 🔒 **Strong, modern cryptography**
  - Argon2 key derivation
  - HMAC-based verification
  - AES-256 encryption at rest
- 🖥️ **Native desktop UI**
  - Built with PySide6 (Qt)
  - No browser, no Electron
- 🧠 **Automatic locking**
  - Locks after inactivity
  - Optional lock on window blur
- ⌨️ **Global hotkey**
  - Instantly bring VaultX to the foreground
- 📋 **Secure clipboard**
  - Auto-clears after timeout
- 📴 **Offline-first by design**
  - No network access
  - No external services
- 🧱 **Single-file executable**
  - Packaged with PyInstaller

---

## 🖼️ Screenshots

### 🔑 Login Screen
![VaultX Login](images/password1.png)

### 🗄️ Vault View
![VaultX Vault](images/password2.png)

---

## 🧱 Architecture Overview

```text
VaultX/
├── main.py                # App entry point
├── config.py              # Global configuration
├── crypto/                # Key derivation + encryption
│   ├── kdf.py
│   └── cipher.py
├── storage/               # Encrypted vault persistence
│   └── vault.py
├── models/                # Data models
│   └── entry.py
├── ui/                    # PySide6 UI components
│   ├── login.py
│   ├── vault_view.py
│   ├── settings_view.py
│   └── theme.qss
├── utils/                 # Clipboard, hotkeys, helpers
│   ├── clipboard.py
│   ├── hotkey.py
│   └── password_gen.py
├── icon/                  # App icons
│   ├── content.png
│   └── content.ico
└── VaultX.spec            # PyInstaller build spec
```

---

## 🔐 Cryptography & Security Model

VaultX encrypts all vault data **at rest** using standard, audited primitives.

### 🔑 Key Derivation

- Master password is **never stored**
- Per-user random salt
- Key derived with **Argon2** (memory-hard)

```text
Master Password
        ↓
   Argon2 KDF
        ↓
  256-bit Master Key
```

Argon2 resists GPU and ASIC cracking far better than PBKDF2.

---

### 🔒 Encryption at Rest

Vault data is encrypted using **AES-256** via the Python `cryptography` library.

- AES-256
- Authenticated encryption (AEAD)
- Unique random nonce per encryption
- Integrity verified on every decrypt

No ECB.  
No custom crypto.  
No silent corruption.

---

### 🧾 Authentication & Verification

- Username protected with **HMAC**
- Verifier confirms correct password
- Constant-time comparisons prevent timing attacks

---

### 🧠 Key Lifetime

- Keys exist **only in memory**
- Re-derived on login
- Destroyed on lock or exit
- Clipboard auto-clears

VaultX does **not**:
- Cache keys
- Store plaintext secrets
- Write decrypted data to disk

---

### 🛡️ Threat Model (Honest)

Protects against:
- Disk theft
- Offline vault exfiltration
- Casual snooping

Does **not** protect against:
- Malware running as you
- Keyloggers
- Compromised OS
- Memory inspection while unlocked

Encryption at rest is not magic.

---

## 🚀 Running from Source

### Requirements
- Python 3.11+
- Windows / Linux / macOS

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

---

## 📦 Building a Single Executable (Windows)

```bash
pyinstaller --onefile --windowed `
  --name VaultX `
  --icon "icon\content.ico" `
  --add-data "icon;icon" `
  --add-data "ui;ui" `
  --add-data "crypto;crypto" `
  --add-data "models;models" `
  --add-data "storage;storage" `
  --add-data "utils;utils" `
  main.py

```

Output:
```text
dist/VaultX.exe
```

---

## 🧭 Philosophy

VaultX is intentionally:
- Offline
- Auditable
- Opinionated
- Boring in the best way

No accounts.  
No sync.  
No tracking.

Just a vault.

---

## 📜 License

MIT License.  
Do whatever you want.  
Just don’t pretend you wrote it.

---

## ⚠️ Disclaimer

This project is for personal use and learning.

Review the code before trusting it with secrets you can’t afford to lose.

Cryptography is hard.  
Confidence without verification is harder.

---

**Built by someone who doesn’t trust browsers with passwords.**
