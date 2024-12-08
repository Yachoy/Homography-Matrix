from pathlib import Path
import os
import cv2

from HomographyMatrixCalculator.ui.WindowMain import *

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    code = app.exec()

    exit(code)


if __name__ == "__main__":
    main()