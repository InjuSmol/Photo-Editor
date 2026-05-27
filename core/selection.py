# core/selection.py
from PySide6.QtCore import QObject, Signal

# Global state for the selected items 

class SelectionManager(QObject):
    selection_changed = Signal(str, list)

    def __init__(self):
        super().__init__()
        self._selections = {
            "photo": set(),
            "print": set(),
        }

    def set_selection(self, tab, files):
        self._selections[tab] = set(files)
        self.selection_changed.emit(tab, list(self._selections[tab]))

    def get(self, tab):
        return list(self._selections.get(tab, []))

    def clear(self, tab):
        self._selections[tab].clear()
        self.selection_changed.emit(tab, [])