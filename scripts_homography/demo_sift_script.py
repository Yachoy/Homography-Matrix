from typing import Tuple
import cv2
import numpy as np

from HomographyMatrixCalculator.backend.backend import PrototypeHomographyComposite


class SIFT(PrototypeHomographyComposite):
    img1: np.array
    img2: np.array

    def calculate_matrix(self) -> Tuple[np.array, np.array]:
        sift = cv2.SIFT_create(
            nfeatures=1500,  # Максимальное кол-во (0 - неограничено)
            nOctaveLayers=5,  # октавы (по умолчанию 3)
            contrastThreshold=0.01,  # Порог контрастности (меньше -> больше точек на слабоконтрастных участках)
            edgeThreshold=5,  # Порог подавления точек на границах (меньше -> лучше избегает ложных граней)
            sigma=1.6  # Sigma гауссиана
        )
        self.kp1, self.des1 = sift.detectAndCompute(self.img1, None)
        self.kp2, self.des2 = sift.detectAndCompute(self.img2, None)

        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = bf.match(self.des1, self.des2)
        matches = sorted(matches, key=lambda x: x.distance)

        src_pts = np.float32([self.kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([self.kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

        return H

    def calculate_image(self, H: np.array) -> np.array:
        return cv2.warpPerspective(self.img2, H, (self.img1.shape[1], self.img1.shape[0]))

    def set_img2(self, image: np.array):
        self.img1 = image.copy()
        return self.img1

    def set_img1(self, image: np.array):
        self.img2 = image.copy()
        return self.img2