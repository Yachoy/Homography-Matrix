import os.path
import numpy as np

from PIL import Image

from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QPixmap, QDrag
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from typing import *
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QFileDialog

import sys


class LabelImageVisualize(QLabel):
    def __init__(self, parent=None, image: np.array = None, text_default: str = ""):
        super().__init__(parent)
        self._image = image
        self._last_pixmap = None
        self._default_text = text_default  # Добавлено поле для текста по умолчанию
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if image is not None:
            self.update_image(image)
        else:
            self.setText(self._default_text)  # Устанавливаем текст по умолчанию, если изображения нет

    def resizeEvent(self, event):
        if self._default_text is None and self._last_pixmap is not None:
            self.setPixmap(self._last_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def update_image(self, image: np.array) -> None:
        self._image = image.copy()
        self._default_text = None

        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        self._last_pixmap = pixmap
        self._update_pixmap(pixmap)


    # private because the class needs _image updating when set image
    def _update_pixmap(self, pixmap: QPixmap):
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled_pixmap)

    def get_image(self) -> np.array:
        if self._image is None:
            return None
        return self._image.copy()

class LabelDropFile(LabelImageVisualize):
    def __init__(self, text_default: str = "", allowed_ext: Tuple[str] = (".jpg", ".png", ".bmp", ".jpeg", ".gif")):
        super().__init__(text_default=text_default)  # Передаем text_default в родительский конструктор
        self._allowed_exts: Tuple[str] = allowed_ext
        self._last_path: Optional[str] = None
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mouseDoubleClickEvent(self, event):
        self.open_file_dialog()
        super().mouseDoubleClickEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():  # Проверяем, что перетаскиваются URL (файлы)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                try:
                    self.setText("")
                    if not self.process_path_file(file_path):  # Исправлено имя метода
                        print("Drop file failed")
                        event.ignore()
                        return
                    event.accept()
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.setText(self._default_text)
                    event.ignore()
        else:
            event.ignore()

    def open_file_dialog(self):
        """Открывает диалог выбора файла."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать изображение",  # Заголовок диалога
            "",  # Директория по умолчанию (пустая - текущая)
            "Изображения (*.png *.jpg *.bmp *.jpeg *.gif);;Все файлы (*)"  # Фильтр файлов
        )

        if file_path:  # Если пользователь выбрал файл
            try:
                self.setText("")
                if not self.process_path_file(file_path):
                    print("Loading file failed")
                    return
            except Exception as e:
                print(f"Error loading image: {e}")
                self.setText(self._default_text)

    @staticmethod
    def _check_file_extension(file_path, allowed_extensions) -> bool:
        _, ext = os.path.splitext(file_path.lower())  # Получаем расширение файла и приводим к нижнему регистру
        return ext in allowed_extensions

    def process_path_file(self, path_file: str) -> bool:
        if not os.path.isfile(path_file):
            print(f"Error: Handled path is not file")
            return False
        if not self._check_file_extension(path_file, self._allowed_exts):
            print(f"File extension is not allowed. List of available extensions: {self._allowed_exts}")
            return False

        try:
            image = Image.open(path_file) # Используем PIL для загрузки
            image_np = np.array(image)

            # Конвертируем в RGB, если нужно
            if image_np.ndim == 2: # Если изображение grayscale
                image_np = np.stack([image_np]*3, axis=-1) # Преобразуем в RGB
            elif image_np.shape[2] == 4: # Если есть альфа-канал
                image_np = image_np[:,:,:3] # Убираем альфа-канал


            self.update_image(image_np)  # Обновляем изображение через метод update_image
            self._last_path = path_file
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False


    def get_last_path(self) -> Optional[str]:
        return self._last_path