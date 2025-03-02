from typing import Tuple
import cv2
import numpy as np

# import PrototypeHomographyComposite (or any another Source code like this)
# there are work because --add-data in building app via pyinstaller
from Source.backend.backend import PrototypeHomographyComposite 


class SIFT(PrototypeHomographyComposite):
    def get_kp_des(self, img):
        #TODO GRAY FORMAT SIFT INPUT
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sift = cv2.SIFT_create(
            nfeatures=1000,  # Максимальное кол-во (0 - неограничено)
            nOctaveLayers=5,  # октавы (по умолчанию 3)
            contrastThreshold=0.01,  # Порог контрастности (меньше -> больше точек на слабоконтрастных участках)
            edgeThreshold=5,  # Порог подавления точек на границах (меньше -> лучше избегает ложных граней)
            sigma=1.6  # Sigma гауссиана
        )
        return sift.detectAndCompute(img, None)

    def match(self, des1, des2):
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = bf.match(des1, des2)
        return sorted(matches, key=lambda x: x.distance)

    def calculate_matrix(self, img1, img2) -> Tuple[np.array, np.array, np.array]:
        kp1, des1 = self.get_kp_des(img1)
        kp2, des2 = self.get_kp_des(img2)
        matches = self.match(des1, des2)

        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        return H, src_pts, dst_pts
