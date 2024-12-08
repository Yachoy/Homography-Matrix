from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys

from HomographyMatrixCalculator.ui.WindowMain import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    code = app.exec()

    exit(code)