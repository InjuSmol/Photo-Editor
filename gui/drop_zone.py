from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter
from pathlib import Path
import shutil

class DropZone(QWidget):
    files_dropped = Signal() 

    def __init__(self, target_folder: Path):
        super().__init__()
        self.target_folder = target_folder

        self.setAcceptDrops(True)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            src = Path(url.toLocalFile())
            if src.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                continue
            shutil.copy2(src, self.target_folder / src.name)

        event.acceptProposedAction()
        self.files_dropped.emit() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.gray)
        painter.drawRect(self.rect().adjusted(5, 5, -5, -5))
        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            "Drag photos here"
        )
