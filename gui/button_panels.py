from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QToolButton, QMenu
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QMenu
)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox


class PhotoPanel(QWidget):
    def __init__(self, selection_manager, file_actions):
        super().__init__()

        self.selection_manager = selection_manager
        self.file_actions = file_actions

        self.logo_position = "top-right"  # default

        layout = QVBoxLayout()
        #layout.addWidget(QLabel("Photo Actions"))

        # ===== Add Logo row =====
        logo_row = QHBoxLayout()

        self.logo_btn = QPushButton("Add Logo")
        self.logo_btn.clicked.connect(self.run_add_logo)

        self.logo_menu_btn = QPushButton("▼")
        self.logo_menu_btn.setFixedWidth(28)

        menu = QMenu(self)

        positions = {
            "Top Left": "top-left",
            "Top Right": "top-right",
            "Bottom Left": "bottom-left",
            "Bottom Right": "bottom-right",
        }


        for label, pos in positions.items():
            action = menu.addAction(label)
            action.triggered.connect(lambda _, p=pos: self.set_logo_position(p))

        self.logo_menu = menu
        self.logo_menu_btn.clicked.connect(self.show_logo_menu)

        from PySide6.QtWidgets import QCheckBox
        self.auto_rotate_logo_checkbox = QCheckBox("Automatically rotate logo")
        self.auto_rotate_logo_checkbox.setChecked(True)

        layout.addWidget(self.logo_btn)
        logo_row.addWidget(self.logo_menu_btn)
        logo_row.addWidget(self.auto_rotate_logo_checkbox) 

        # ===== Move to Print =====
        self.print_btn = QPushButton("Move to Print")
        self.print_btn.clicked.connect(self.move_to_print)

        # ===== Auto-print checkbox =====
        from PySide6.QtWidgets import QCheckBox
        self.auto_print_checkbox = QCheckBox("Automatically print on move to print")
        self.auto_print_checkbox.setChecked(True)

        layout.addLayout(logo_row)
        layout.addWidget(self.print_btn)
        layout.addWidget(self.auto_print_checkbox)  # <--- add it here
        layout.addStretch()

        self.setLayout(layout)

    def move_to_print(self):
        files = self.selection_manager.get("photo")
        auto_print = self.auto_print_checkbox.isChecked()  # now exists!
        self.file_actions.move_to_print(files, auto_print=auto_print)

    # ===== Actions =====
        
    def show_logo_menu(self):
        self.logo_menu.exec(
            self.logo_menu_btn.mapToGlobal(
                self.logo_menu_btn.rect().bottomLeft()
            )
        )

    def set_logo_position(self, position):
        self.logo_position = position
        self.logo_btn.setText(f"Add Logo ({position})")

    def run_add_logo(self):
        files = self.selection_manager.get("photo")
        auto_rotate_logo = self.auto_rotate_logo_checkbox.isChecked()
        self.file_actions.add_logo(files, self.logo_position, auto_rotate_logo=auto_rotate_logo)
"""
    def move_to_print(self):
        files = self.selection_manager.get("photo")
        auto_print = self.auto_print_checkbox.isChecked()  # read from the panel itself
        self.file_actions.move_to_print(files, auto_print=auto_print)
"""

class PrintPanel(QWidget):
    def __init__(self, selection_manager, file_actions, photo_panel=None):
        super().__init__()

        self.selection_manager = selection_manager
        self.file_actions = file_actions
        self.photo_panel = photo_panel  # store reference

        layout = QVBoxLayout()
        #layout.addWidget(QLabel("Print Actions"))

        # Send selected files (or all) to printer
        self.send_btn = QPushButton("Send to Printer")
        self.send_btn.clicked.connect(self.send_to_printer)

        layout.addWidget(self.send_btn)
        layout.addStretch()
        self.setLayout(layout)

    def send_to_printer(self):
        # get auto_print value directly from photo_panel
        #auto_print = self.photo_panel.auto_print_checkbox.isChecked() if self.photo_panel else True
        selected_files = self.selection_manager.get("print")
        self.file_actions.send_to_printer(selected_files)

    def queue_for_print(self):
        files = self.selection_manager.get("print")
        self.file_actions.move_to_print(files)
        auto_print = self.parent().parent().parent().parent().auto_print_enabled
        if auto_print:
            self.file_actions.send_to_printer(files)