import os
os.environ['QT_API'] = 'pyside6'

import pathlib
from pathlib import Path
import cv2
from .ui.WindowMain import *

def main():
    root_path = pathlib.Path(__file__).resolve().parent

    # От греха за конкуренцию между matplotlib, pyside6 и cv2 за backend QT
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    win = MainWindow(root_path)
    win.show()
    code = app.exec()
<<<<<<< HEAD
    
=======
>>>>>>> cb476ba2a37ae22a086591e9aa7b157ba431fff0
