import os
import importlib.util
import inspect
import numpy as np
from typing import *
from abc import abstractmethod


class PrototypeHomographyComposite:
    @abstractmethod
    def set_img1(self, image: np.array) -> np.array:
        raise NotImplementedError

    @abstractmethod
    def set_img2(self, image: np.array) -> np.array:
        raise NotImplementedError

    @abstractmethod
    def calculate_matrix(self) -> Tuple[np.array, np.array]:
        raise NotImplementedError

    @abstractmethod
    def calculate_image(self, matrix: np.array) -> np.array:
        raise NotImplementedError


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

        for name, obj in inspect.getmembers(module):  # Перебираем все члены модуля
            if inspect.isclass(obj) and issubclass(obj, PrototypeHomographyComposite) and obj != PrototypeHomographyComposite:
                try:
                    self.calculator = obj()  # Создаем экземпляр калькулятора
                    print(f"Loaded homography calculator: {name} from {self.path_to_script}")
                    return  # Выходим после нахождения первого подходящего класса
                except Exception as e:
                    print(f"Error instantiating calculator {name}: {e}")
                    #  Возможно, стоит пропустить ошибку и искать дальше, или raise, если нужен только один корректный класс

        if self.calculator is None:
            raise ValueError(f"No suitable homography calculator found in {self.path_to_script}")



    def set_img1(self, image: np.array) -> Optional[np.array]:
        if self.calculator:
            return self.calculator.set_img1(image)
        return None


    def set_img2(self, image: np.array) -> Optional[np.array]:
        if self.calculator:
            return self.calculator.set_img2(image)
        return None

    def calculate_matrix(self) -> Optional[Tuple[np.array, np.array]]:
        if self.calculator:
            return self.calculator.calculate_matrix()
        return None


    def calculate_image(self, matrix: np.array) -> Optional[np.array]:
        if self.calculator:
            return self.calculator.calculate_image(matrix)
        return None

    def update_calculator_script(self):
        self._load_calculator()
