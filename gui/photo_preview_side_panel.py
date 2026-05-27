# the side panel for the photo editor:

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSlider, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QWheelEvent, QImage
from pathlib import Path
from PySide6.QtWidgets import QSizePolicy
from PIL import Image


def create_slider(self, name: str):
    label = QLabel(name)
    label.setStyleSheet("color: white;")

    slider = QSlider(Qt.Horizontal)
    slider.setRange(-100, 100)
    slider.setValue(0)

    value_label = QLabel("0")
    value_label.setStyleSheet("color: #aaa;")

    slider.valueChanged.connect(
        lambda v, l=value_label: l.setText(str(v))
    )
    slider.valueChanged.connect(self.apply_edits)

    box = QVBoxLayout()
    box.addWidget(label)
    box.addWidget(slider)
    box.addWidget(value_label)

    return box, slider