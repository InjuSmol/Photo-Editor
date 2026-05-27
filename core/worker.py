from PySide6.QtCore import QObject, Signal

class Worker(QObject):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        while self._running:
            ...
        self.finished.emit()

    def stop(self):
        self._running = False
