from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sys
import numpy as np


class ImageViewer(QWidget):
    def __init__(self, canvas1, canvas2, image):
        super().__init__()

        self.canvas1 = canvas1
        self.canvas2 = canvas2
        self.image = image

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image and Plots Viewer")

        # Графики
        plots_layout = QVBoxLayout()
        plots_layout.addWidget(self.canvas1)
        plots_layout.addWidget(self.canvas2)

        # Изображение
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Основной layout
        main_layout = QHBoxLayout(self)
        main_layout.addLayout(plots_layout)
        main_layout.addWidget(self.image_label, stretch=1) # stretch=1 позволяет изображению занимать оставшееся пространство

        self.load_image()
        self.setLayout(main_layout)
        self.show()

    def load_image(self):
        pixmap = self.get_pixmap(self.image)
        self.update_image(pixmap)

    def get_pixmap(self, image):
        if isinstance(image, str):
            return QPixmap(image)
        elif isinstance(image, QPixmap):
            return image.copy()
        elif isinstance(image, np.ndarray):  # Поддержка numpy массивов
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            return QPixmap.fromImage(qImg)
        else:
            return QPixmap()

    def update_image(self, pixmap):

        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        pixmap = self.get_pixmap(self.image)
        self.update_image(pixmap)
        super().resizeEvent(event)
