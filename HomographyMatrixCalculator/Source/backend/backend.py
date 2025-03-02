import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import os
import importlib.util
import inspect
import pathlib
import cv2
import numpy as np
from typing import *
from abc import abstractmethod
from PySide6.QtGui import QPixmap


def plot_errors_of_points(src_pts, dst_pts):
    """
    Рассчитывает евклидово расстояние между точками и создает FigureCanvas
    для отображения графика ошибок.

    Args:
        src_pts (np.ndarray): Массив координат исходных точек.
        dst_pts (np.ndarray): Массив координат соответствующих точек.

    Returns:
        FigureCanvas: Экземпляр FigureCanvas, содержащий график ошибок.
    """

    # Рассчитать евклидово расстояние между точками
    errors = np.linalg.norm(src_pts - dst_pts, axis=2)

    min_error = np.min(errors)
    max_error = np.max(errors)
    mean_error = np.mean(errors)
    print(f"Min: {min_error}, Max: {max_error}, Mean: {mean_error}")

    fig, ax = plt.subplots(figsize=(8, 6))  # Создаем Figure и Axes объекты

    ax.plot(errors, label="Error per Point", color="blue")
    ax.axhline(y=min_error, color="green", linestyle="--", label=f"Min Error: {min_error:.2f}")
    ax.axhline(y=mean_error, color="orange", linestyle="--", label=f"Mean Error: {mean_error:.2f}")
    ax.axhline(y=max_error, color="red", linestyle="--", label=f"Max Error: {max_error:.2f}")

    ax.set_title("Error Between src_pts and dst_pts")
    ax.set_xlabel("Point Index")
    ax.set_ylabel("Error")
    ax.legend()
    ax.grid()

    canvas = FigureCanvas(fig)  # Создаем FigureCanvas из Figure
    return canvas


def generate_points(image_width, image_height, num_points):
    """Генерирует N точек, равномерно распределенных по изображению."""
    x = np.random.uniform(0, image_width, num_points)
    y = np.random.uniform(0, image_height, num_points)
    return np.column_stack((x, y))


def calculate_reprojection_errors(H1, H2, points):
    """Вычисляет ошибки репроекции для заданных точек и матриц гомографии."""
    points_hom = np.concatenate((points, np.ones((points.shape[0], 1))), axis=1)

    projected_points1 = (H1 @ points_hom.T).T
    projected_points1 = projected_points1[:, :2] / projected_points1[:, 2:]

    projected_points2 = (H2 @ points_hom.T).T
    projected_points2 = projected_points2[:, :2] / projected_points2[:, 2:]

    errors = np.linalg.norm(projected_points1 - projected_points2, axis=1)
    return errors


def plot_reprojection_errors(errors, points):
    """Создает график ошибок репроекции, включая среднюю ошибку."""
    fig, ax = plt.subplots()
    sc = ax.scatter(points[:, 0], points[:, 1], c=errors, cmap='viridis')
    fig.colorbar(sc, label='Ошибка репроекции')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Ошибки репроекции')

    # Вычисляем и добавляем среднюю ошибку
    mean_error = np.mean(errors)
    ax.axhline(mean_error, color='red', linestyle='--', label=f'Средняя ошибка: {mean_error:.2f}')
    ax.legend()  # Обновляем легенду, чтобы включить среднюю ошибку

    canvas = FigureCanvas(fig)
    return canvas


class PrototypeHomographyComposite:
    @abstractmethod
    def get_kp_des(self, img: np.array):
        raise NotImplementedError

    @abstractmethod
    def match(self, des1, des2):
        raise NotImplementedError

    @abstractmethod
    def calculate_matrix(self, img1, img2) -> Tuple[np.array, np.array, np.array]:
        raise NotImplementedError

    @staticmethod
    def calculate_image(img, matrix: np.array) -> np.array:
        return cv2.warpPerspective(img, matrix, (img.shape[1], img.shape[0]))


class CompositeHomographyCalculator:
    def __init__(self, ):
        self.calculator: Optional[PrototypeHomographyComposite] = None
        self.path_to_script = ""

    def choose_calculator(self, path_to_script: str):
        self.path_to_script = path_to_script
        self._load_calculator()

    def _load_calculator(self):
        """Загружает калькулятор из указанного скрипта."""

        if not os.path.exists(self.path_to_script):
            raise FileNotFoundError(f"Script not found: {self.path_to_script}")

        module_name = os.path.splitext(os.path.basename(self.path_to_script))[0]

        spec = importlib.util.spec_from_file_location(module_name, self.path_to_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, PrototypeHomographyComposite) and obj != PrototypeHomographyComposite:
                try:
                    self.calculator = obj()
                    print(f"Loaded homography calculator: {name} from {self.path_to_script}")
                    return
                except Exception as e:
                    print(f"Error instantiating calculator {name}: {e}")

        if self.calculator is None:
            raise ValueError(f"No suitable homography calculator found in {self.path_to_script}")

    def calculate_matrix(self, img1, img2) -> Optional[Tuple[np.array, np.array, np.array]]:
        if self.calculator:
            return self.calculator.calculate_matrix(img1, img2)

    def calculate_image(self, img, matrix: np.array) -> Optional[np.array]:
        if self.calculator:
            return self.calculator.calculate_image(img, matrix)

    def update_calculator_script(self):
        self._load_calculator()

    def get_kp_des(self, img: np.array):
        if self.calculator:
            return self.calculator.get_kp_des(img)
