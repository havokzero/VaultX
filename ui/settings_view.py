# ui/settings_view.py

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QGroupBox,
)
from PySide6.QtCore import Qt


class SettingsView(QWidget):
    def __init__(self, change_master_cb):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # --- Security ---
        security = QGroupBox("Security")
        sec_layout = QVBoxLayout(security)

        change_btn = QPushButton("Change Master Password")
        change_btn.clicked.connect(change_master_cb)
        sec_layout.addWidget(change_btn)

        layout.addWidget(security)

        # --- Behavior ---
        behavior = QGroupBox("Behavior")
        beh_layout = QVBoxLayout(behavior)

        beh_layout.addWidget(QLabel("Auto-lock timeout (minutes):"))
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)
        self.timeout.setValue(3)
        beh_layout.addWidget(self.timeout)

        layout.addWidget(behavior)

        layout.addStretch()
