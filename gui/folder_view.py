from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
from pathlib import Path
from PIL import Image
import config
from PySide6.QtCore import QTimer
import shutil
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyle

from gui.photo_preview_window import PhotoPreviewWindow

# Folde View Class: 
class FolderView(QListWidget):
    def __init__(
        self,
        folder_path: Path,
        *,
        tab_name: str,
        selection_manager,
        enable_drop=False,
        shutdown_manager=None
    ):
        super().__init__()

        self.folder_path = folder_path
        self.tab_name = tab_name
        self.selection_manager = selection_manager
        self.enable_drop = enable_drop
        self.view_mode = "icon"

        self.itemDoubleClicked.connect(self.open_preview)

        self.setSelectionMode(QListWidget.ExtendedSelection)

        if enable_drop:
            self.setAcceptDrops(True)
            self.viewport().setAcceptDrops(True)
            self.setDragDropMode(QListWidget.DropOnly)
            self.setDefaultDropAction(Qt.CopyAction)

        '''
        if enable_drop:
            self.setAcceptDrops(True)
            self.setDragDropMode(QListWidget.DropOnly)
        '''
        self.setFocusPolicy(Qt.StrongFocus)
        self.set_icon_mode()

        self.itemSelectionChanged.connect(self._on_selection_changed)

        # AUTO REFRESH every second
        self.timer = QTimer() # TODO: need to replace the polling with something else
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)

        if shutdown_manager:
            shutdown_manager.shutdown_requested.connect(self.shutdown)


        self.refresh()

    def open_preview(self, item):
        # Collect all image files in this folder
        files = [
            f for f in sorted(self.folder_path.iterdir())
            if f.suffix.lower() in config.IMAGE_EXTS
        ]

        clicked_path = Path(item.data(Qt.UserRole))

        if clicked_path not in files:
            return

        index = files.index(clicked_path)

        self.preview = PhotoPreviewWindow(files, index)
        self.preview.show()

    def _on_selection_changed(self):
        if not self.selection_manager or not self.tab_name:
            return

        selected_files = [
            self.folder_path / item.text()
            for item in self.selectedItems()
        ]

        self.selection_manager.set_selection(
            self.tab_name,
            selected_files
        )
    # Clear button used by X button: 
    def clear_selection(self):
        tab = self.current_tab_name()
        if not tab:
            return

        self.selection_manager.clear(tab)

        if tab == "photo":
            self.photo.clear_selection()
        elif tab == "print":
            self.print.clear_selection()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.count() == 0 and self.enable_drop:
            painter = QPainter(self.viewport())
            painter.setPen(Qt.gray)
            painter.drawText(
                self.viewport().rect(),
                Qt.AlignCenter,
                "Drag Photos Here"
            )

    def shutdown(self):
        if self.timer.isActive():
            self.timer.stop()
        print("[INFO] FolderView stopped")


# Drag & Drop Support (Incoming tab):

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            src = Path(url.toLocalFile())

            if not src.exists():
                continue

            if src.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                continue

            dest = self.folder_path / src.name
            shutil.copy2(src, dest)

        event.acceptProposedAction()
        self.refresh()

# Icon View vs. List View Toggle: 

    def set_icon_mode(self):
        self.view_mode = "icon"
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(120, 120))
        self.setGridSize(QSize(140, 160))
        self.setSpacing(10)
    
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setWrapping(True)


    def set_list_mode(self):
        self.view_mode = "list"
        self.setViewMode(QListWidget.ListMode)
        self.setIconSize(QSize(32, 32))

    # Populate Items (with tubnails + filenames): 
    def refresh(self):
        if not self.folder_path.exists():
            return

        # Block selection signals while rebuilding UI
        self.blockSignals(True)
        self.clear()

        selected_names = set()
        if self.selection_manager and self.tab_name:
            selected_names = {
                f.name for f in self.selection_manager.get(self.tab_name)
            }

        for file in sorted(self.folder_path.iterdir()):
            if file.name.startswith("."):
                continue

            item = QListWidgetItem(file.name)

            # STORE FULL PATH HERE
            item.setData(Qt.UserRole, str(file))

            if file.is_dir():
                item.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
            elif file.suffix.lower() in config.IMAGE_EXTS:
                icon = self.make_thumbnail(file)
                if icon:
                    item.setIcon(icon)

            self.addItem(item)

            # Restore selection from global state
            if file.name in selected_names:
                item.setSelected(True)

        # Re-enable signals
        self.blockSignals(False)
        
# Thumbnail Generation (Fast & Safe): 
    # PIL --> uses PIL TODO: what is PIL even? 
    # Changed so that i dont need PIL anymore
    def make_thumbnail(self, path: Path):
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return None

        return QIcon(pixmap.scaled(
            128, 128,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

        