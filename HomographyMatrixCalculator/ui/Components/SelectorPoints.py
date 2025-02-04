import sys
import numpy as np
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QApplication
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QFont, QKeyEvent, QResizeEvent, QWheelEvent, QTransform, QPainterPath
from PySide6.QtCore import Qt, QPointF, QSize, QPoint


class ImageWidget(QGraphicsView):
    def __init__(self, image_array, callback):
        super().__init__()

        self.callback = callback
        self.points = [None] * 4
        self.image_array = image_array
        self.zoom_factor = 1

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.pixmap_item = self.set_image(image_array)
        self.scene.addItem(self.pixmap_item)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)  # Important for zoom/pan
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setFocusPolicy(Qt.StrongFocus)

    def set_image(self, image_array):
        height, width, channel = image_array.shape
        bytes_per_line = channel * width
        q_image = QImage(image_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        return pixmap_item

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in [Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3, Qt.Key.Key_4]:
            if not self.isEnabled():
                return
            point_index = int(event.text()) - 1
            mouse_pos = self.mapToScene(self.mapFromGlobal(self.cursor().pos()))
            x = mouse_pos.x()
            y = mouse_pos.y()

            # Get pixmap from pixmap_item
            if self.pixmap_item:   # Check if pixmap_item exists
                self.points[point_index] = (x, y) # Use scene coordinates directly

                if all(p is not None for p in self.points):
                    self.callback(self.points)
                    self.setEnabled(False)

            self.update()  # Redraw to show the points


    def wheelEvent(self, event: QWheelEvent):
        if not self.hasFocus():
            return

        degrees = event.angleDelta().y() / 8
        steps = degrees / 15

        if steps > 0:
            self.zoom_factor *= 1.25
        else:
            self.zoom_factor /= 1.25

        self.scale(1.25 if steps > 0 else 0.8, 1.25 if steps > 0 else 0.8)


    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        pen = QPen(Qt.red, 2)  # Fixed pen width
        painter.setPen(pen)

        font = QFont()
        font_size = 10  # Fixed font size
        font.setPointSize(font_size)
        painter.setFont(font)

        for i, point in enumerate(self.points):
            if point is not None:
                x, y = point
                scene_point = QPointF(x, y)
                view_point = self.mapFromScene(scene_point)

                # Calculate scaled offset for text
                text_offset = QPoint(5, -5)  # Adjust as needed

                # Draw the ellipse (fixed size)
                radius = 3 # Or whatever size you want
                painter.drawEllipse(view_point, radius, radius)  # Fixed-size ellipse
                painter.drawText(view_point + text_offset, str(i + 1)) # No need to change the text position here since we are already working in viewport space

        painter.end()



class SelectPointsWindow(QMainWindow):
    def __init__(self, image1_array, image2_array, callback):
        super().__init__()
        self.setWindowTitle("Image Point Selector")
        self.callback = callback
        self.image1_array = image1_array
        self.image2_array = image2_array

        self.points_image1 = []
        self.points_image2 = []

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # Left image with callback for points
        self.image1_widget = ImageWidget(self.image1_array, self.process_points_image1)

        # Right image with callback for points
        self.image2_widget = ImageWidget(self.image2_array, self.process_points_image2)

        layout.addWidget(self.image1_widget, stretch=1)  # Add stretch factor
        layout.addWidget(self.image2_widget, stretch=1)  # Add stretch factor

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.setMinimumSize(QSize(200, 100))  # Set a reasonable minimum size

    def process_points_image1(self, points):
        self.points_image1 = points
        #print(f"Selected points on Image 1: {self.points_image1}")
        if len(self.points_image1) == 4:
            self.on_points_selected()

    def process_points_image2(self, points):
        self.points_image2 = points
        #print(f"Selected points on Image 2: {self.points_image2}")
        if len(self.points_image2) == 4:
            self.on_points_selected()

    def normalize_points(self, points, widget):
        """
        Normalize points to the range [0, 1] relative to the widget's image dimensions.
        """
        pixmap = widget.pixmap()
        if not pixmap:
            return points

        width = pixmap.width()
        height = pixmap.height()
        normalized = [(x / width, y / height) for x, y in points]
        return normalized

    def on_points_selected(self):
        """
        Placeholder function called after four points are selected on both images.
        """
        if len(self.points_image1) == 4 and len(self.points_image2) == 4:
            # Example: Passing both point sets to a separate function
            self.callback(self.points_image1, self.points_image2)
            self.destroy()
            self.close()
