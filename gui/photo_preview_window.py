from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSlider
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QWheelEvent, QImage
from pathlib import Path
from PySide6.QtWidgets import QSizePolicy
from PIL import Image
import shutil
import re
import config

from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import QRectF, QPointF
from PIL.ImageQt import ImageQt


from core.editor import (
    apply_brightness_to_image,
    apply_contrast_to_image,
    apply_gamma_to_image,
    apply_sharpness_to_image,
)

class PhotoPreviewWindow(QWidget):
    def __init__(self, files, start_index=0):
        super().__init__()

        self.files = files
        self.index = start_index
        self.current_edited_pil = None
        #self.index = 0 # TODO: do I really need that? 

        self.zoom = 1.0
        
        self.min_zoom = 0.55
        self.max_zoom = 2.0   
        
        self.original_pixmap = None

        self.resize(900, 700)
        self.init_ui()
        self.load_image()

    # ---------- UI ----------
    def init_ui(self):
        main_layout = QHBoxLayout(self)

        viewer_layout = QVBoxLayout()
        main_layout.addLayout(viewer_layout, 1)

        # Top bar: shows filename and counter
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        viewer_layout.addWidget(self.title_label)

        '''
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: black;")

        self.image_label.setMinimumSize(1, 1)
        self.image_label.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Ignored
        )

        self.image_label.setScaledContents(False)
        viewer_layout.addWidget(self.image_label, 1)
        '''
        self.crop_view = CropGraphicsView() # new
        self.crop_view.safe_padding_ratio = config.SAFE_PADDING
        self.crop_view.show_center_lines = config.SHOW_CENTER_LINES
        self.crop_view.viewport().update()
        viewer_layout.addWidget(self.crop_view, 1) # new
        '''self.image_label.setSizePolicy( # do I need to keep this? 
            QSizePolicy.Ignored,
            QSizePolicy.Ignored
        )'''

        # Bottom controls
        controls = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.next_btn = QPushButton("▶")
        self.zoom_out_btn = QPushButton("−")
        self.zoom_in_btn = QPushButton("+")
        self.zoom_label = QLabel()  # shows zoom percentage

        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn.clicked.connect(self.next_image)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        self.zoom_label.setStyleSheet("color: white;")
        self.update_zoom_label()

        controls.addWidget(self.prev_btn)
        controls.addWidget(self.next_btn)
        controls.addStretch()
        controls.addWidget(self.zoom_out_btn)
        controls.addWidget(self.zoom_in_btn)
        controls.addWidget(self.zoom_label)

        ######### added (start)
        side_panel = QFrame()
        side_panel.setFixedWidth(220)
        side_panel.setStyleSheet("background: #1e1e1e;")

        panel_layout = QVBoxLayout(side_panel)
        panel_layout.setAlignment(Qt.AlignTop)

        main_layout.addWidget(side_panel)
        ######## addded (end) 


        self.brightness_slider = None
        self.contrast_slider = None
        self.gamma_slider = None
        self.sharpness_slider = None

        for name, attr in [
            ("Brightness", "brightness_slider"),
            ("Contrast", "contrast_slider"),
            ("Gamma", "gamma_slider"),
            ("Sharpness", "sharpness_slider"),
        ]:
            box, slider = self.create_slider(name)
            panel_layout.addLayout(box)
            setattr(self, attr, slider)

        self.sharpness_slider.setRange(0,300)
        self.sharpness_slider.setValue(0)
        panel_layout.addSpacing(20)

        self.save_btn = QPushButton("Save (Press Enter)")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setMinimumHeight(50)

        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #A8E6A3;
                color: black;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #95D892;
            }
        """)

        panel_layout.addWidget(self.save_btn)
        
        """### Added (start)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_image)
        controls.addWidget(self.save_btn)
        #### added (en"""

        viewer_layout.addLayout(controls) ## TODO: do i need to change it to viewer_layout.addWidget(

    # ---------- Image ----------
    '''
    def extract_raw_number(self, filename: str) -> int:
        """Extract the number from raw_[number]_... filename"""
        m = re.match(r"raw_(\d+)", filename)
        if m:
            return int(m.group(1))
        return self.index + 1  # fallback to index if no number found
    '''
    def extract_raw_number(self, filename: str) -> int:
        """
        Extract the only number from filename.
        Example:
            logo_logo2.jpg -> 2
            test15.png -> 15
            img100.jpeg -> 100
        """
        match = re.search(r"\d+", filename)
        if match:
            return int(match.group())
        return None  # or raise ValueError if you prefer
    '''
    def save_image(self): # new
        if not self.current_edited_pil:
            return

        path: Path = self.files[self.index]

        cropped = self.crop_view.get_cropped_pil(self.current_edited_pil)

        cropped.save(path, quality=95)

        self.original_pil = cropped
        self.current_edited_pil = cropped
        self.original_pixmap = QPixmap(str(path))

        self.render_image()

        print("Image overwritten with crop + edits") 
    '''

    '''
    def save_image(self):
        if not self.files or not self.current_edited_pil:
            return

        path: Path = self.files[self.index]
        parent = path.parent

        # ---- old_ph folder ----
        old_dir = parent / "old_ph"
        old_dir.mkdir(exist_ok=True)

        # Move original file into old_ph
        old_path = old_dir / path.name
        if path.exists():
            path.rename(old_path)

        # ---- save edited image ----
        new_name = f"edit_raw_{self.raw_number}{path.suffix}"
        out_path = parent / new_name

        self.current_edited_pil.save(out_path, quality=95)

        # Update current path to edited image for future operations
        self.files[self.index] = out_path
        self.original_pixmap = QPixmap(str(out_path))
        self.original_pil = Image.open(out_path).convert("RGB")
        self.current_edited_pil = self.original_pil.copy()

        self.render_image()

        print(f"Original moved to: {old_path}")
        print(f"Edited image saved as: {out_path}")
    '''

    
    def save_image(self):
        
        if not hasattr(self, "original_pil") or self.original_pil is None:
            return

        path: Path = self.files[self.index]

        cropped, was_cropped = self.crop_view.get_cropped_pil(self.original_pil)

        if was_cropped:
            # Save cropped image
            cropped.save(path, quality=95)

            # Record that this image was cropped
            raw_number = self.extract_raw_number(path.name)
            config.CROPPED_IMAGES[raw_number] = True

            # Update current state
            self.original_pil = cropped
            self.current_edited_pil = cropped
            self.original_pixmap = QPixmap.fromImage(ImageQt(cropped))
            
            #  Mark the view as cropped and refit
            self.crop_view.is_cropped_image = True
            self.crop_view.set_image(self.original_pixmap)
            self.crop_view.refit_image_to_crop()

            print(f"Image saved and refitted: {raw_number}")

        else:
            # If no crop, just overwrite current pixmap
            self.original_pixmap = QPixmap(str(path))
            self.crop_view.set_image(self.original_pixmap)
            self.render_image()


    def pil_to_qpixmap(pil_img):
        return QPixmap.fromImage(ImageQt(pil_img))
    '''
    def load_image(self):
        if not self.files:
            return

        path: Path = self.files[self.index]

        raw_number = self.extract_raw_number(path.name)

        is_cropped = config.CROPPED_IMAGES.get(raw_number, False)
        self.crop_view.is_cropped_image = is_cropped
        
        self.original_pil = Image.open(path).convert("RGB")
        self.original_pixmap = QPixmap(str(path))

        # Set pixmap in CropGraphicsView
        self.crop_view.set_image(self.original_pixmap)
        
        if is_cropped:
            #cropped, _ = self.crop_view.get_cropped_pil(self.original_pil)
            #self.original_pil = cropped
            #self.current_edited_pil = cropped
            #self.original_pixmap = QPixmap.fromImage(ImageQt(cropped))
            self.crop_view.set_image(self.original_pixmap)  # update view to cropped version

        self.update_title()
        self.update_zoom_label()
        self.apply_edits()
    '''
    def load_image(self):
        path = self.files[self.index]

        self.original_pil = Image.open(path).convert("RGB")
        self.current_edited_pil = self.original_pil.copy()

        self.original_pixmap = QPixmap(str(path))
        self.crop_view.set_image(self.original_pixmap)

        raw_number = self.extract_raw_number(path.name)
        self.crop_view.is_cropped_image = config.CROPPED_IMAGES.get(raw_number, False)

        self.apply_edits()
    '''
    def render_image(self):
        if not self.original_pixmap or self.original_pixmap.isNull():
            return

        w = int(self.original_pixmap.width() * self.zoom)
        h = int(self.original_pixmap.height() * self.zoom)

        scaled = self.original_pixmap.scaled(
            w,
            h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled)
    '''
    def render_image(self): # New
        if not self.original_pixmap:
            return

        self.crop_view.set_image(self.original_pixmap)

    def apply_edits(self):
        if not hasattr(self, "original_pil"):
            return

        # update global/persistent state
        config.CURRENT_EDITS["brightness"] = self.brightness_slider.value()
        config.CURRENT_EDITS["contrast"] = self.contrast_slider.value()
        config.CURRENT_EDITS["gamma"] = self.gamma_slider.value()
        config.CURRENT_EDITS["sharpness"] = self.sharpness_slider.value()

        img = self.original_pil

        b = 1.0 + config.CURRENT_EDITS["brightness"] / 100
        c = 1.0 + config.CURRENT_EDITS["contrast"] / 100
        s = 1.0 + config.CURRENT_EDITS["sharpness"] / 50
        g = max(0.1, 1.0 + config.CURRENT_EDITS["gamma"] / 100)

        img = apply_brightness_to_image(img, b)
        img = apply_contrast_to_image(img, c)
        img = apply_sharpness_to_image(img, s)
        img = apply_gamma_to_image(img, g)

        self.current_edited_pil = img
        self.update_preview_from_pil(img)
        
    def update_preview_from_pil(self, pil_img: Image.Image):
        qt_image = ImageQt(pil_img)
        self.original_pixmap = QPixmap.fromImage(qt_image)

        # IMPORTANT: do NOT call set_image()
        self.crop_view.pixmap_item.setPixmap(self.original_pixmap)

    # ---------- UI helpers ----------
    def update_title(self):
        path: Path = self.files[self.index]
        counter_text = f"{self.index + 1} / {len(self.files)}"
        self.title_label.setText(f"Preview ({path.name})       {counter_text}")

    def update_zoom_label(self):
        percent = int(self.zoom * 100)
        self.zoom_label.setText(f"{percent}%")

    
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

    # ---------- Navigation ----------
    def next_image(self):
        if self.index < len(self.files) - 1:
            self.index += 1
            self.load_image()

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.load_image()

    # ---------- Zoom ----------
    """
    def compute_fit_zoom(self):
        if not self.original_pixmap:
            return 1.0

        label_w = self.image_label.width()
        label_h = self.image_label.height()

        if label_w == 0 or label_h == 0:
            return 1.0

        img_w = self.original_pixmap.width()
        img_h = self.original_pixmap.height()

        zoom_w = label_w / img_w
        zoom_h = label_h / img_h

        return min(zoom_w, zoom_h)
    """
    def zoom_in(self):
        self.set_zoom(self.zoom * 1.2)

    def zoom_out(self):
        self.set_zoom(self.zoom / 1.2)

    def set_zoom(self, new_zoom: float):
        # clamp zoom to limits
        self.zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        self.update_zoom_label()
        self.render_image()
    

    # Use wheel or trackpad
    '''
    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    '''

    # ---------- Events ----------
    """
    def resizeEvent(self, event):
        if hasattr(self, "original_pixmap") and self.original_pixmap:
            self.zoom = self.compute_fit_zoom()
            self.update_zoom_label()
        self.render_image()
    """
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.prev_image()
        elif event.key() in (Qt.Key_Plus, Qt.Key_Equal):
            self.zoom_in()
        elif event.key() == Qt.Key_Minus:
            self.zoom_out()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.save_image()



from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QWheelEvent
from PIL import Image
from PySide6.QtGui import QPainterPath, QColor
from PySide6.QtWidgets import QGraphicsPathItem

class CropGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.user_has_moved = False # new new new
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setStyleSheet("background: black; border: none;")

        self.setTransformationAnchor(QGraphicsView.NoAnchor) # new new
        self.setResizeAnchor(QGraphicsView.NoAnchor) # new new

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Safe area and central lines: 
        self.safe_padding_ratio = 0.1   # default 10%
        self.show_center_lines = True   # default ON

        # new: 
        self.handle_size = 12
        self.active_handle = None
        self.resizing = False

        self.is_cropped_image = False

        
        # Scene & pixmap
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene_obj.addItem(self.pixmap_item)
        
        # Crop rectangle (fixed)
        self.crop_rect = QRectF()
        
        # Drag & zoom
        self._drag_pos = None
        self.current_zoom = 1.0
        self.min_zoom = 0.55
        self.max_zoom = 2.0
        
        # Overlay
        #self.overlay_item = QGraphicsPathItem()
        #self.overlay_item.setBrush(QColor(0, 0, 0))  # black outside
        #self.overlay_item.setPen(Qt.NoPen)
        #self.overlay_item.setZValue(10)  # on top
        #self.scene_obj.addItem(self.overlay_item)
        
        self.setMouseTracking(True)

    def get_image_rect_scene(self):
        rect = self.pixmap_item.boundingRect()
        return self.pixmap_item.mapToScene(rect).boundingRect()
            
    def update_crop_rect(self):
        view_rect = self.viewport().rect()
        margin = 0.2  # 5% margin

        if (
            self.pixmap_item.pixmap() is not None
            and not self.pixmap_item.pixmap().isNull()
        ):
            img_w = self.pixmap_item.pixmap().width()
            img_h = self.pixmap_item.pixmap().height()
            img_aspect = img_w / img_h
        else:
            img_aspect = 2 / 3  # fallback

        # ------------------------------
        # Decide orientation properly
        # ------------------------------
        if img_aspect >= 1:  # horizontal OR square
            crop_ratio = 3 / 2
        else:  # vertical
            crop_ratio = 2 / 3

        # ------------------------------
        # Compute largest rect that fits
        # ------------------------------
        max_w = view_rect.width() * (1 - margin)
        max_h = view_rect.height() * (1 - margin)

        w = max_w
        h = w / crop_ratio

        if h > max_h:
            h = max_h
            w = h * crop_ratio

        x = view_rect.center().x() - w / 2
        y = view_rect.center().y() - h / 2

        self.crop_rect = QRectF(x, y, w, h)

        self.viewport().update()
            
    def set_image(self, pixmap: QPixmap):
        self.pixmap_item.setPixmap(pixmap)

        # Reset transforms
        self.pixmap_item.setScale(1.0)
        self.pixmap_item.setPos(0, 0)
        self.current_zoom = 1.0

        self.scene_obj.setSceneRect(QRectF(pixmap.rect()))
        self.update_crop_rect()

        self.user_has_moved = False
        self.refit_image_to_crop()

        '''
        # CRITICAL: reset previous transforms
        self.pixmap_item.setScale(1.0)
        self.pixmap_item.setPos(0, 0)
        self.current_zoom = 1.0

        self.scene_obj.setSceneRect(QRectF(pixmap.rect()))

        self.update_crop_rect()

        crop_w, crop_h = self.crop_rect.width(), self.crop_rect.height()
        img_w, img_h = pixmap.width(), pixmap.height()

        scale_x = crop_w / img_w
        scale_y = crop_h / img_h

        scale = max(scale_x, scale_y) * 1.05

        self.pixmap_item.setTransformOriginPoint(img_w / 2, img_h / 2)
        self.pixmap_item.setScale(scale)

        # Center correctly
        img_center = self.pixmap_item.mapToScene(pixmap.rect().center())
        crop_center = self.mapToScene(self.crop_rect.center().toPoint())

        delta = crop_center - img_center
        self.pixmap_item.moveBy(delta.x(), delta.y())

        self.current_zoom = scale
        '''

    def wheelEvent(self, event: QWheelEvent):
        """Smooth zoom, clamped."""
        delta = event.angleDelta().y() / 120  # normalize per notch
        zoom_step = 1.05
        factor = zoom_step ** delta
        new_zoom = self.current_zoom * factor
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        self.current_zoom = new_zoom
        self.user_has_moved = True
        #self.scale(factor, factor)
        self.pixmap_item.setScale(new_zoom)

    def resetTransform(self):
        """Reset zoom & position."""
        self.current_zoom = 1.0
        self.pixmap_item.setScale(1.0)
        self.pixmap_item.setPos(0, 0)
        self.centerOn(self.pixmap_item)
    
    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        img_rect = self.get_image_rect_scene()

        corners = {
            "tl": img_rect.topLeft(),
            "tr": img_rect.topRight(),
            "bl": img_rect.bottomLeft(),
            "br": img_rect.bottomRight(),
        }

        for name, point in corners.items():
            handle_rect = QRectF(
                point.x() - self.handle_size / 2,
                point.y() - self.handle_size / 2,
                self.handle_size,
                self.handle_size
            )
            if handle_rect.contains(scene_pos):
                self.active_handle = name
                self.resizing = True
                self._drag_pos = scene_pos
                return

        # fallback to move
        self._drag_pos = scene_pos
        super().mousePressEvent(event)  

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())

        if self.resizing and self.active_handle:
            delta = scene_pos - self._drag_pos
            self._drag_pos = scene_pos

            # Use vertical movement only (more stable)
            scale_factor = 1.0 + delta.y() / 300

            new_scale = self.pixmap_item.scale() * scale_factor

            if 0.2 < new_scale < 5:
                self.pixmap_item.setScale(new_scale)

            return

        # otherwise move image
    # otherwise move image
        if self._drag_pos and not self.resizing:
            delta = scene_pos - self._drag_pos
            self._drag_pos = scene_pos
            self.pixmap_item.moveBy(delta.x(), delta.y())
            self.user_has_moved = True
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.active_handle = None
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def drawForeground(self, painter, rect):
        painter.setRenderHint(QPainter.Antialiasing)

        # ---------------------------
        # 1️ Draw resize handles (SCENE space)
        # ---------------------------
        img_rect = self.get_image_rect_scene()

        painter.setBrush(QColor("white"))
        painter.setPen(Qt.NoPen)

        for point in [
            img_rect.topLeft(),
            img_rect.topRight(),
            img_rect.bottomLeft(),
            img_rect.bottomRight(),
        ]:
            handle_rect = QRectF(
                point.x() - self.handle_size / 2,
                point.y() - self.handle_size / 2,
                self.handle_size,
                self.handle_size,
            )
            painter.drawRect(handle_rect)
        
        img_rect = self.get_image_rect_scene()

        # ---- White frame around photo ----
        frame_pen = QPen(QColor("white"))
        frame_pen.setWidth(1) # or 2 for thinner
        painter.setPen(frame_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(img_rect)


        # ---------------------------
        # 2️ Switch to VIEWPORT space
        # ---------------------------
        painter.save()
        painter.resetTransform()

        view_rect = self.viewport().rect()

        full_path = QPainterPath()
        full_path.addRect(view_rect)

        crop_path = QPainterPath()
        crop_path.addRect(self.crop_rect)

        overlay_path = full_path.subtracted(crop_path)

        painter.fillPath(overlay_path, QColor(0, 0, 0, 220))

        pen = QPen(QColor("green"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)  
        painter.drawRect(self.crop_rect)

                # ---- Safe Area ----
        # ---- Safe Area (based on shortest side) ----
        if self.safe_padding_ratio > 0:
            shortest_side = min(self.crop_rect.width(), self.crop_rect.height())
            pad = shortest_side * self.safe_padding_ratio

            safe_rect = QRectF(
                self.crop_rect.left() + pad,
                self.crop_rect.top() + pad,
                self.crop_rect.width() - 2 * pad,
                self.crop_rect.height() - 2 * pad
            )

            safe_pen = QPen(QColor("green"))
            safe_pen.setWidth(1)
            safe_pen.setStyle(Qt.DashLine)
            painter.setPen(safe_pen)
            painter.drawRect(safe_rect)
        
        # ---- Center Cross Lines ----
        if self.show_center_lines:
            center_pen = QPen(QColor("green"))
            center_pen.setWidth(1)
            center_pen.setStyle(Qt.DashLine)
            painter.setPen(center_pen)

            cx = self.crop_rect.center().x()
            cy = self.crop_rect.center().y()

            # Vertical line
            painter.drawLine(cx, self.crop_rect.top(), cx, self.crop_rect.bottom())

            # Horizontal line
            painter.drawLine(self.crop_rect.left(), cy,
                            self.crop_rect.right(), cy)

        painter.restore()
            
    def get_cropped_pil(self, pil_image: Image.Image):
        """Return the crop based strictly on the crop rectangle, ignoring zoom/margin."""

        if pil_image is None:
            return None

        # Get pixmap (actual image) size
        pixmap_w = self.pixmap_item.pixmap().width()
        pixmap_h = self.pixmap_item.pixmap().height()

        # Map crop_rect in scene/view coords to pixmap coordinates
        top_left = self.mapToScene(self.crop_rect.topLeft().toPoint())
        bottom_right = self.mapToScene(self.crop_rect.bottomRight().toPoint())

        pix_tl = self.pixmap_item.mapFromScene(top_left)
        pix_br = self.pixmap_item.mapFromScene(bottom_right)

        # Scale to PIL coordinates
        img_w, img_h = pil_image.size
        x1 = int(pix_tl.x() * img_w / pixmap_w)
        y1 = int(pix_tl.y() * img_h / pixmap_h)
        x2 = int(pix_br.x() * img_w / pixmap_w)
        y2 = int(pix_br.y() * img_h / pixmap_h)

        # Clamp
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img_w, x2), min(img_h, y2)

        if x1 == 0 and y1 == 0 and x2 == img_w and y2 == img_h:
            # No real crop happened
            return pil_image, False

        cropped = pil_image.crop((x1, y1, x2, y2))
        return cropped, True
    
    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.update_crop_rect()

        # Only auto-refit if user has NOT adjusted image
        if not self.user_has_moved and not self.pixmap_item.pixmap().isNull():
            self.refit_image_to_crop()

    def refit_image_to_crop(self):
        pixmap = self.pixmap_item.pixmap()
        if pixmap.isNull():
            return

        crop_w = self.crop_rect.width()
        crop_h = self.crop_rect.height()

        img_w = pixmap.width()
        img_h = pixmap.height()

        scale_x = crop_w / img_w
        scale_y = crop_h / img_h

        # 🔥 THE IMPORTANT PART
        if self.is_cropped_image:
            # Fit entirely inside crop rectangle
            scale = min(scale_x, scale_y)
        else:
            # Force overflow outside crop rectangle
            scale = max(scale_x, scale_y) * 1.15

        self.pixmap_item.setTransformOriginPoint(img_w / 2, img_h / 2)
        self.pixmap_item.setScale(scale)

        # Center image inside crop rectangle
        img_center = self.pixmap_item.mapToScene(pixmap.rect().center())
        crop_center = self.mapToScene(self.crop_rect.center().toPoint())

        delta = crop_center - img_center
        self.pixmap_item.moveBy(delta.x(), delta.y())

        self.current_zoom = scale