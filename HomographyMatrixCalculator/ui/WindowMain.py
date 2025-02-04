import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import time
import traceback
from datetime import datetime

from PIL.ImageQt import QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QFileDialog
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtCore import QSize

import sys
from typing import *
import numpy as np
from PySide6.QtGui import QImage, QPixmap
import cv2
import itertools
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)

from HomographyMatrixCalculator.ui.design.ui_Win import Ui_MainWindow
from HomographyMatrixCalculator.ui.Components.Label import LabelDropFile, LabelImageVisualize
from HomographyMatrixCalculator.ui.Components.VisualiseDuoImages import ImageViewer
from HomographyMatrixCalculator.ui.Components.Table import TableWidgetCopy
from HomographyMatrixCalculator.backend.backend import (
    CompositeHomographyCalculator,
    plot_errors_of_points,
    plot_reprojection_errors,
    generate_points,
    calculate_reprojection_errors
)
from HomographyMatrixCalculator.ui.Components.SelectorPoints import SelectPointsWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    calculator: CompositeHomographyCalculator = None

    def __init__(self, root_path):
        self.root_path = root_path
        super().__init__()
        self._result_win = QWidget() #window visualise auto test
        self.calculator = CompositeHomographyCalculator()
        self.setupUi(self)

        # remake labels to drag-drop-vis labels -------------
        self.verticalLayout_3.removeWidget(self.label)
        self.verticalLayout_4.removeWidget(self.label_2)
        self.label.hide()
        self.label_2.hide()

        self.left_drop_image_label = LabelDropFile("Drop or chose a img...")
        self.right_drop_image_label = LabelDropFile("Drop or chose a img...")

        self.verticalLayout_3.addWidget(self.left_drop_image_label)
        self.verticalLayout_4.addWidget(self.right_drop_image_label)
        # ---------------------------------------------------

        # remake label to vis label for Homography image visualisation --------------------
        self.verticalLayout.removeWidget(self.label_5)
        self.label_5.hide()

        self.homography_fixed_image_label = LabelImageVisualize("Homography applied img...")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.homography_fixed_image_label.setSizePolicy(sizePolicy3)
        self.homography_fixed_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.homography_fixed_image_label)
        #----------------------------------------------------

        # remake table make able to copy for past to the excel.
        self.verticalLayout_5.removeWidget(self.tableWidget)
        self.tableWidget.hide()

        self.homography_matrix_table = TableWidgetCopy()
        if (self.homography_matrix_table.columnCount() < 4):
            self.homography_matrix_table.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.homography_matrix_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.homography_matrix_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.homography_matrix_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.homography_matrix_table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        if (self.homography_matrix_table.rowCount() < 3):
            self.homography_matrix_table.setRowCount(3)
        self.homography_matrix_table.setObjectName(u"tableWidget")

        self.homography_matrix_table.setMinimumSize(QSize(0, 120))
        self.homography_matrix_table.setMaximumSize(QSize(485, 120))

        self.verticalLayout_5.insertWidget(0, self.homography_matrix_table)
        #-----------------------------------------------------


        #--------------REFER TABLE-----------------------
        self.verticalLayout_5.removeWidget(self.tableWidget_2)
        self.tableWidget_2.hide()

        self.refer_matrix_table = TableWidgetCopy(self.centralwidget)
        if (self.refer_matrix_table.columnCount() < 4):
            self.refer_matrix_table.setColumnCount(4)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.refer_matrix_table.setHorizontalHeaderItem(0, __qtablewidgetitem1)
        if (self.refer_matrix_table.rowCount() < 3):
            self.refer_matrix_table.setRowCount(3)
        self.refer_matrix_table.setObjectName(u"tableWidget_2")
        self.refer_matrix_table.setMinimumSize(QSize(0, 120))
        self.refer_matrix_table.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_5.insertWidget(1, self.refer_matrix_table)

        ___qtablewidgetitem = self.homography_matrix_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Calculate", None))
        ___qtablewidgetitem1 = self.refer_matrix_table.horizontalHeaderItem(0)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Refer", None))

        self._signals()

    def _signals(self):
        self.pushButton_2.clicked.connect(self._choose_calculator)
        self.BtnGenerateAuto.clicked.connect(self._calculate_matrix_auto_clicked)
        self.BtnGenerateRefer.clicked.connect(self._calculate_matrix_refer_clicked)
        self.startAutoTestBtn.clicked.connect(self._auto_test)

    @staticmethod
    def show_warning_message(parent=None, title="Warning", message="This is a warning message."):
        """
        Displays a warning message box.

        Args:
            parent: The parent widget of the message box. If None, the message box is shown as a top-level window.
            title: The title of the message box.
            message: The text of the warning message.
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)  # Icon for warning
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)  # Only OK button
        msg_box.exec()

    def get_matrix_at(self, table) -> Optional[np.array]:
        matrix = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                item = table.item(i, j+1)
                if item is not None:
                    matrix[i, j] = float(item.text())
                else:
                    return None
        return matrix

    def generate_reference_matrix(self):
        img1 = self.left_drop_image_label.get_image()
        img2 = self.right_drop_image_label.get_image()
        if img1 is None:
            return self.show_warning_message(self, message="You didn't choose first file img!")
        if img2 is None:
            return self.show_warning_message(self, message="You didn't choose second file img!")

        def get_normalized_points_callback(points1, points2):
            print(f"Get points {points1, points2}")
            points1 = np.array(points1, dtype=np.float32)
            points2 = np.array(points2, dtype=np.float32)
            H, mask = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)

            if H is None:
                print("Не удалось вычислить матрицу гомографии для refer.")
                return

            for i in range(3):
                for j in range(3):
                    el = QTableWidgetItem()
                    el.setText(f"{H[i, j]:.4f}")
                    self.refer_matrix_table.setItem(i, j + 1, el)


        self._w = SelectPointsWindow(img1, img2, get_normalized_points_callback)
        self._w.show()

    def _choose_calculator(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать калькулятор",
            "",
            "Python script (*.py);;Все файлы (*)"
        )

        if file_path:  # Если пользователь выбрал файл
            self.calculator.choose_calculator(file_path)


    def _calculate_matrix_auto_clicked(self):
        if self.calculator.calculator is None:
            return self.show_warning_message(self, message="You didn't choose any scripts for calculating!")
        try:
            self.calculator.update_calculator_script()
            img1 = self.left_drop_image_label.get_image()
            img2 = self.right_drop_image_label.get_image()
            if img1 is None:
                return self.show_warning_message(self, message="You didn't choose first file img!")
            if img2 is None:
                return self.show_warning_message(self, message="You didn't choose second file img!")

            H, src_pts, dst_pts = self.calculator.calculate_matrix(img2, img1)

            for i in range(3):
                for j in range(3):
                    el = QTableWidgetItem()
                    el.setText(str(H[i][j]))
                    self.homography_matrix_table.setItem(i, j+1, el)

            img = self.calculator.calculate_image(img2, H)
            self.homography_fixed_image_label.update_image(img)

        except Exception as e:
            print("While executing script cauth a error: ",e)
            print("Full error:")
            traceback.print_exc()

    def _calculate_matrix_refer_clicked(self):
        if self.calculator.calculator is None:
            return self.show_warning_message(self, message="You didn't choose any scripts for calculating!")
        try:
            self.calculator.update_calculator_script()
            img1 = self.left_drop_image_label.get_image()
            img2 = self.right_drop_image_label.get_image()
            if img1 is None:
                return self.show_warning_message(self, message="You didn't choose first file img!")
            if img2 is None:
                return self.show_warning_message(self, message="You didn't choose second file img!")

            self.generate_reference_matrix()
            H = self.get_matrix_at(self.refer_matrix_table)
            if H is None:
                return
            img = self.calculator.calculate_image(img2, H)
            self.homography_fixed_image_label.update_image(img)

        except Exception as e:
            print("While executing script cauth a error: ",e)
            print("Full error:")
            traceback.print_exc()


    def _auto_test(self):
        is_need_to_use_reference =  self.checkBoxReference.isChecked()
        is_need_to_save_attempts = self.checkBoxAttempts.isChecked()

        img1, img2 = None, None
        if self.calculator.calculator is None:
            return self.show_warning_message(self, message="You didn't choose any scripts for calculating!")
        try:
            self.calculator.update_calculator_script()
            img1 = self.left_drop_image_label.get_image()
            img2 = self.right_drop_image_label.get_image()
            if img1 is None:
                return self.show_warning_message(self, message="You didn't choose first file img!")
            if img2 is None:
                return self.show_warning_message(self, message="You didn't choose second file img!")
        except Exception as e:
            traceback.print_exc()
            return

        H, src, dst = self.calculator.calculate_matrix(img2, img1)
        H_refer = None
        if is_need_to_use_reference:
            H_refer = self.get_matrix_at(self.refer_matrix_table)
            if H_refer is None:
                H_refer = self.get_matrix_at(self.refer_matrix_table)
                if H_refer is None:
                    return
        else:
            H_refer = self.get_matrix_at(self.homography_matrix_table)
            if H_refer is None:
                H_refer = self.get_matrix_at(self.homography_matrix_table)
                if H_refer is None:
                    return

        img_h = self.calculator.calculate_image(img2, H)
        print(img2.shape)
        img_referH = self.calculator.calculate_image(img2, H_refer)

        _, src_pts, dst_pts = self.calculator.calculate_matrix(img_h, img_referH)

        for i in range(3):
            for j in range(3):
                el = QTableWidgetItem()
                el.setText(str(H[i][j]))
                self.homography_matrix_table.setItem(i, j+1, el)

        #generate plots
        # file_plot_path = f"{self.root_path}/testing/{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.png"
        plot_pts_err = plot_errors_of_points(src_pts, dst_pts)


        points = generate_points(img2.shape[1], img2.shape[0], 100)
        errors = calculate_reprojection_errors(H, H_refer, points)
        plot_reprojection_err = plot_reprojection_errors(errors, points)


        height, width, channel = img_referH.shape
        bytes_per_line = 3 * width
        q_image = QImage(img_referH.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        self._result_win = ImageViewer(
            plot_pts_err,
            plot_reprojection_err,
            QPixmap.fromImage(q_image)
        )

        self._result_win.show()

        return
