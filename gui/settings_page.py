from PySide6.QtWidgets import (
    QApplication, QWidget, QStackedLayout,
    QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QTabWidget, QListWidget, QTabWidget, QHBoxLayout, QMessageBox, QCheckBox
)
import config
from pathlib import Path

from PySide6.QtWidgets import QSpinBox, QFileDialog

class SettingsPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.general_tab = GeneralSettingsTab()
        self.logo_tab = LogoSettingsTab()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.logo_tab, "Logo")

        layout.addWidget(self.tabs)

        # Bottom buttons
        btns = QHBoxLayout()
        btns.addStretch()

        save_btn = QPushButton("Save")
        back_btn = QPushButton("Back")

        save_btn.clicked.connect(self.save_settings)
        back_btn.clicked.connect(self.go_back)

        btns.addWidget(back_btn)
        btns.addWidget(save_btn)

        layout.addLayout(btns)

    def save_settings(self):
        self.general_tab.apply()
        self.logo_tab.apply()
        print("[INFO] Settings saved")

    def go_back(self):
        self.app.show_dashboard()

class GeneralSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.workspace = FolderPicker("Workspace", config.WORKSPACE)
        self.incoming = FolderPicker("Incoming", config.INCOMING)
        self.photo = FolderPicker("Photo", config.PHOTO_DIR)
        self.print = FolderPicker("Print", config.PRINT_DIR)
        self.printer = FolderPicker("Printer", config.PRINTER_DIR)
        self.session = FolderPicker("Session Base", config.SESSION_BASE_DIR)

        for w in [
            self.workspace, self.incoming, self.photo,
            self.print, self.printer, self.session
        ]:
            layout.addWidget(w)
        
        self.safe_padding_spin = QSpinBox()
        self.safe_padding_spin.setRange(0, 50)
        self.safe_padding_spin.setValue(10)  # default 10%
        self.safe_padding_spin.setSuffix("%")

        self.center_lines_checkbox = QCheckBox("Show center guide lines")
        self.center_lines_checkbox.setChecked(True)

        layout.addWidget(QLabel("Safe Area Padding"))
        layout.addWidget(self.safe_padding_spin)
        layout.addWidget(self.center_lines_checkbox)

        layout.addStretch()

    def apply(self):
        config.WORKSPACE = self.workspace.value()
        config.INCOMING = self.incoming.value()
        config.PHOTO_DIR = self.photo.value()
        config.PRINT_DIR = self.print.value()
        config.PRINTER_DIR = self.printer.value()
        config.SESSION_BASE_DIR = self.session.value()

        config.SAFE_PADDING = self.safe_padding_spin.value() / 100
        config.SHOW_CENTER_LINES = self.center_lines_checkbox.isChecked()

class LogoSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Logo picker
        self.logo_edit = QLineEdit(str(config.LOGO_PATH))
        browse = QPushButton("Browse Logo")

        browse.clicked.connect(self.pick_logo)

        row = QHBoxLayout()
        row.addWidget(QLabel("Logo File"))
        row.addWidget(self.logo_edit)
        row.addWidget(browse)

        layout.addLayout(row)

        # Size %
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 100)
        self.size_spin.setValue(13)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Default Size (%)"))
        size_row.addWidget(self.size_spin)

        layout.addLayout(size_row)

        # Margin %
        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(0, 100)
        self.margin_spin.setValue(7)

        margin_row = QHBoxLayout()
        margin_row.addWidget(QLabel("Default Margin (%)"))
        margin_row.addWidget(self.margin_spin)

        layout.addLayout(margin_row)

        layout.addStretch()

    def pick_logo(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Logo",
            str(config.WORKSPACE),
            "Images (*.png *.jpg *.jpeg)"
        )
        if file:
            self.logo_edit.setText(file)

    def apply(self):
        config.LOGO_PATH = Path(self.logo_edit.text())
        config.LOGO_SIZE_PERCENT = self.size_spin.value()
        config.LOGO_MARGIN_PERCENT = self.margin_spin.value()


class FolderPicker(QWidget):
    def __init__(self, label, initial_path):
        super().__init__()
        self.path = initial_path

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel(label))

        self.edit = QLineEdit(str(initial_path))
        browse = QPushButton("Browse")

        browse.clicked.connect(self.pick_folder)

        layout.addWidget(self.edit)
        layout.addWidget(browse)

    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder", self.edit.text()
        )
        if folder:
            self.edit.setText(folder)

    def value(self):
        return Path(self.edit.text())