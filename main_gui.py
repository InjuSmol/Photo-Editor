# GUI launcher 

# ~~~~~~~~~~~~~~~~~~~~~~ IMPORTS: ~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QStackedLayout,
    QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QTabWidget, QListWidget, QTabWidget, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor # TODO: what is widget
from core.file_manager import ensure_dirs
from PySide6.QtCore import QTimer # TODO: QTimer 
# -> refresh folder content ----> for polling every 1 sec
from core.watcher import WatcherThread
import sys

from gui.folder_view import FolderView
import config
from gui.drop_zone import DropZone
from core.shutdown import ShutdownManager
from core.selection import SelectionManager

from PySide6.QtWidgets import QSplitter
from gui.button_panels import PhotoPanel, PrintPanel
from core.file_actions import FileActionManager
from gui.settings_page import SettingsPage

from datetime import datetime
import config

from pathlib import Path

# ~~~~~~~~~~~~~~~~~~~~~~ START PAGE: ~~~~~~~~~~~~~~~~~~~~~~~~~
class StartPage(QWidget):
    def __init__(self, switch_callback):
        super().__init__()

        layout = QVBoxLayout()

        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your name")

        self.session_input = QLineEdit()
        self.session_input.setPlaceholderText("Session name")

        start_btn = QPushButton("START")
        start_btn.clicked.connect(
            lambda: switch_callback(
                self.name_input.text(),
                self.session_input.text()
            )
        )

        layout.addWidget(QLabel("VISTA Photo System"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.session_input)
        layout.addWidget(start_btn)

        self.setLayout(layout)

        
"""
class Dashboard(QWidget):
    def __init__(self, shutdown_manager, selection_manager):

        super().__init__()
        self.shutdown_manager = shutdown_manager
        self.selection_manager = selection_manager

        layout = QVBoxLayout()
        tabs = QTabWidget()

        self.drop_zone = DropZone(config.INCOMING)

        self.incoming_view = FolderView(
            config.INCOMING,
            tab_name=None,
            selection_manager=None,
            shutdown_manager=shutdown_manager
        )

        self.photo = FolderView(
            config.PHOTO_DIR,
            tab_name="photo",
            selection_manager=self.selection_manager,
            shutdown_manager=shutdown_manager
        )

        self.print = FolderView(
            config.PRINT_DIR,
            tab_name="print",
            selection_manager=self.selection_manager,
            shutdown_manager=shutdown_manager
        )
        incoming_layout = QVBoxLayout()
        incoming_layout.setContentsMargins(0, 0, 0, 0)
        incoming_layout.setSpacing(0)

        incoming_layout.addWidget(self.drop_zone, stretch=1)
        #incoming_layout.addWidget(self.incoming_view, stretch=0)

        incoming_tab = QWidget()
        incoming_tab.setLayout(incoming_layout)

        tabs.addTab(incoming_tab, "Incoming")
        tabs.addTab(self.photo, "Photo")
        tabs.addTab(self.print, "Print")

        layout.addWidget(tabs)
        
        # ====== END SHIFT BUTTON ======
        self.end_shift_btn = QPushButton("End Shift")
        self.end_shift_btn.clicked.connect(self.request_end_shift)
        layout.addWidget(self.end_shift_btn)

        self.setLayout(layout)

        # Connect drop zone -> refresh incoming view
        self.drop_zone.files_dropped.connect(self.incoming_view.refresh)

        # Selection status widget
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("color: #007AFF; font-weight: 500")

        self.clear_btn = QPushButton("✕")
        self.clear_btn.setFixedWidth(28)
        self.clear_btn.setStyleSheet("color: red; font-weight: bold")
        self.clear_btn.clicked.connect(self.clear_selection)

        selection_bar = QHBoxLayout()
        selection_bar.addWidget(self.selection_label)
        selection_bar.addWidget(self.clear_btn)
        selection_bar.addStretch()

        layout.addLayout(selection_bar)

        self.selection_manager.selection_changed.connect(self.update_selection_ui)

    def clear_selection(self):
        tab = self.current_tab_name()
        if tab:
            self.selection_manager.clear(tab)

    def current_tab_name(self):
        index = self.findChild(QTabWidget).currentIndex()
        return {1: "photo", 2: "print"}.get(index)

    def update_selection_ui(self, tab, files):
        if tab != self.current_tab_name():
            return

        count = len(files)

        if count == 0:
            self.selection_label.setText("")
            self.clear_btn.hide()
        else:
            self.selection_label.setText(f"{count} selected")
            self.clear_btn.show()
    """

class Dashboard(QWidget):
    def __init__(self, shutdown_manager, selection_manager):
        super().__init__()


        self.shutdown_manager = shutdown_manager
        self.selection_manager = selection_manager

        #session_folder = Path(config.SESSION_BASE_DIR) / datetime.now().strftime("%Y-%m-%d")
        #session_folder.mkdir(parents=True, exist_ok=True)


        # Added (start)
        self.file_actions = FileActionManager(
            photo_dir=config.PHOTO_DIR,
            print_dir=config.PRINT_DIR,
            old_dir=config.OLD_PH,
            printer_dir=config.PRINTER_DIR,  # <-- make sure this is in config
            session_dir=None                  # we'll set this later in start_session
        )
        # Added (end)

        # ===== ROOT LAYOUT =====
        layout = QVBoxLayout()
        tabs = QTabWidget()

        # ===== INCOMING TAB =====
        self.drop_zone = DropZone(config.INCOMING)

        self.incoming_view = FolderView(
            config.INCOMING,
            tab_name=None,
            selection_manager=None,
            shutdown_manager=shutdown_manager
        )

        incoming_layout = QVBoxLayout()
        incoming_layout.setContentsMargins(0, 0, 0, 0)
        incoming_layout.setSpacing(0)
        incoming_layout.addWidget(self.drop_zone)

        incoming_tab = QWidget()
        incoming_tab.setLayout(incoming_layout)

        # ===== PHOTO TAB =====
        self.photo = FolderView(
            config.PHOTO_DIR,
            tab_name="photo",
            selection_manager=self.selection_manager,
            shutdown_manager=shutdown_manager
        )

        # new added
        photo_panel = PhotoPanel(self.selection_manager, self.file_actions)
        # Update App's global auto_print_enabled when PhotoPanel checkbox changes

        #self.photo_panel = photo_panel  # <--- add this line

        photo_splitter = QSplitter()
        photo_splitter.addWidget(self.photo)
        photo_splitter.addWidget(photo_panel)
        photo_splitter.setStretchFactor(0, 3)
        photo_splitter.setStretchFactor(1, 1)

        # ===== PRINT TAB =====
        self.print = FolderView(
            config.PRINT_DIR,
            tab_name="print",
            selection_manager=self.selection_manager,
            shutdown_manager=shutdown_manager
        )
        self.photo_panel = PhotoPanel(self.selection_manager, self.file_actions)
        self.print_panel = PrintPanel(self.selection_manager, self.file_actions, self.photo_panel)
        #self.print_panel = PrintPanel(self.selection_manager, self.file_actions)

        print_splitter = QSplitter()
        print_splitter.addWidget(self.print)
        print_splitter.addWidget(self.print_panel)
        print_splitter.setStretchFactor(0, 3)
        print_splitter.setStretchFactor(1, 1)

        # ===== ADD TABS =====
        tabs.addTab(incoming_tab, "Incoming")
        tabs.addTab(photo_splitter, "Photo")
        tabs.addTab(print_splitter, "Print")

        layout.addWidget(tabs)

        # ===== END SHIFT BUTTON =====
        self.end_shift_btn = QPushButton("End Shift")
        self.end_shift_btn.clicked.connect(self.request_end_shift)
        layout.addWidget(self.end_shift_btn)

         # ===== SETTINGS BUTTON =====
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_btn)

        # ===== SELECTION BAR =====
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("color: #007AFF; font-weight: 500")

        self.clear_btn = QPushButton("✕")
        self.clear_btn.setFixedWidth(28)
        self.clear_btn.setStyleSheet("color: red; font-weight: bold")
        self.clear_btn.clicked.connect(self.clear_selection)
        self.clear_btn.hide()

        selection_bar = QHBoxLayout()
        selection_bar.addWidget(self.selection_label)
        selection_bar.addWidget(self.clear_btn)
        selection_bar.addStretch()

        layout.addLayout(selection_bar)

        self.setLayout(layout)

        # ===== SIGNALS =====
        self.drop_zone.files_dropped.connect(self.incoming_view.refresh)
        self.selection_manager.selection_changed.connect(self.update_selection_ui)

    # ================= HELPERS =================
        
    def open_settings(self):
        app = self.window()
        if hasattr(app, "open_settings"):
            app.open_settings()

    def request_end_shift(self):
        app = self.window()
        if hasattr(app, "close"):
            app.close()

    def current_tab_name(self):
        tabs = self.findChild(QTabWidget)
        index = tabs.currentIndex()
        return {1: "photo", 2: "print"}.get(index)

    def clear_selection(self):
        tab = self.current_tab_name()
        if tab:
            self.selection_manager.clear(tab)

    def update_selection_ui(self, tab, files):
        if tab != self.current_tab_name():
            return

        count = len(files)
        if count == 0:
            self.selection_label.setText("")
            self.clear_btn.hide()
        else:
            self.selection_label.setText(f"{count} selected")
            self.clear_btn.show()

# Toggle View Buttons: 
    def set_icon_view(self):
        for view in [self.incoming_view, self.photo, self.print]:
            view.set_icon_mode()
            view.refresh()

    def set_list_view(self):
        for view in [self.incoming_view, self.photo, self.print]:
            view.set_list_mode()
            view.refresh()
    
    def request_end_shift(self):
        app = self.window()
        if hasattr(app, "end_shift"):
            app.close()  # triggers App.closeEvent → confirmation → end_shift

    '''
    # Shutdown architecture: 
   End Shift button OR window X
            ↓
    App.closeEvent()
            ↓
    Confirm dialog
            ↓
    end_shift()
            ↓
    - stop timers
    - stop watcher
    - stop workers
    - emit shutdown_requested
    - cleanup folders
            ↓
    QApplication.quit()
    '''
    """
    def confirm_shutdown(self):
        # 'self' is the parent QWidget
        reply = QMessageBox.question(
            self,  # parent
            "End Shift",  # title
            "Are you sure you want to end the shift?",  # message
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # buttons
            QMessageBox.StandardButton.No  # default button
        )

        if reply != QMessageBox.StandardButton.Yes:
            print("[INFO] Shutdown cancelled")
            return

        # Stop watcher thread safely before FolderViews
        if self.watcher_thread and self.watcher_thread.isRunning():
            self.watcher_thread.stop()
            self.watcher_thread.wait()

        # Emit shutdown signal to clean up FolderViews
        self.shutdown_manager._is_shutting_down = True
        self.shutdown_manager.shutdown_requested.emit()
"""

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.auto_print_enabled = True  # default value

        self.selection_manager = SelectionManager()
        self.shutdown_manager = ShutdownManager()
        self._shutting_down = False

        self.stack = QStackedLayout()

        self.start_page = StartPage(self.start_session)
        self.dashboard = Dashboard(self.shutdown_manager, self.selection_manager)

        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.dashboard)
        self.setLayout(self.stack)

        # Connect the checkbox to this global state:
        # Instead of print_panel, use photo_panel
        self.dashboard.photo_panel.auto_print_checkbox.stateChanged.connect(
            lambda state: setattr(self, "auto_print_enabled", state == Qt.Checked)
        )

        self.settings_page = SettingsPage(self) # settings page
        self.stack.addWidget(self.settings_page) # settings page


        self.setWindowTitle("VISTA")
        self.resize(700, 500)

        self.watcher_thread = None

        # Central shutdown handling
        #self.shutdown_manager.shutdown_requested.connect(self.confirm_shutdown)

    def open_settings(self):
        self.stack.setCurrentWidget(self.settings_page)

    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)

    def start_session(self, name, session):
        if not name or not session:
            print("Name and session name required")
            return

        print("SESSION STARTED:")
        print(name, session)

        # 1. Create session folder: e.g., base/session/YYYY-MM-DD_Name_Restaurant
        session_name = f"{datetime.now():%m.%d.%Y} {name} {session}"
        session_folder = Path(config.SESSION_BASE_DIR) / session_name
        session_folder.mkdir(parents=True, exist_ok=True)

        # Save it somewhere globally accessible if needed
        config.CURRENT_SESSION_DIR = session_folder  # <-- dynamic session folder

        # 2. Ensure other directories exist
        ensure_dirs(name, session)

        # After creating the session folder
        self.dashboard.file_actions.set_session_dir(session_folder)

        # 3. Start watcher in background
        self.watcher_thread = WatcherThread()
        self.watcher_thread.start()

        # 4. Pass session folder to Dashboard's FileActionManager
        self.dashboard.file_actions.set_session_dir(session_folder)

        # 5. Switch UI
        self.stack.setCurrentWidget(self.dashboard)

    def end_shift(self):
        print("[INFO] Ending shift...")

        # 1️. Stop watcher thread
        if self.watcher_thread and self.watcher_thread.isRunning():
            print("[INFO] Stopping watcher thread")
            self.watcher_thread.stop()
            self.watcher_thread.wait(3000)

        # 2️. Emit shutdown signal (FolderViews stop timers here)
        print("[INFO] Notifying views to shut down")
        self.shutdown_manager.shutdown_requested.emit()

        # 3️. Cleanup folders
        self.shutdown_manager.cleanup_session()

        print("[INFO] Session ended cleanly")

        QApplication.quit()
       

    def closeEvent(self, event):
        # If shutdown already confirmed, don't ask again
        if getattr(self, "_shutting_down", False):
            event.accept()
            return

        reply = QMessageBox.question(
            self,
            "End Shift",
            "Are you sure you want to end the shift?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._shutting_down = True
            event.accept()
            self.end_shift()
        else:
            event.ignore()


app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())


# Usage of the select option: 
"""
selected = self.selection_manager.get("photo")

if selected:
    files_to_edit = selected
else:
    files_to_edit = list(config.PHOTO_DIR.iterdir())
"""
