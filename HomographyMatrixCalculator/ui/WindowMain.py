import traceback

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

from HomographyMatrixCalculator.ui.design.ui_Win import Ui_MainWindow
from HomographyMatrixCalculator.ui.Components.Label import LabelDropFile, LabelImageVisualize
from HomographyMatrixCalculator.ui.Components.Table import TableWidgetCopy
from HomographyMatrixCalculator.backend.backend import CompositeHomographyCalculator

class MainWindow(QMainWindow, Ui_MainWindow):

    calculator: CompositeHomographyCalculator = None

    def __init__(self):
        super().__init__()
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
        font1 = QFont()
        font1.setPointSize(12)
        self.homography_matrix_table = TableWidgetCopy()
        if (self.homography_matrix_table.columnCount() < 4):
            self.homography_matrix_table.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font1)
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
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.homography_matrix_table.sizePolicy().hasHeightForWidth())
        self.homography_matrix_table.setSizePolicy(sizePolicy1)
        self.homography_matrix_table.setMinimumSize(QSize(485, 0))
        self.homography_matrix_table.setMaximumSize(QSize(485, 120))
        font2 = QFont()
        font2.setPointSize(13)
        self.homography_matrix_table.setFont(font2)

        self.verticalLayout_5.addWidget(self.homography_matrix_table)
        #-----------------------------------------------------

        self._signals()

    def _signals(self):
        self.pushButton_2.clicked.connect(self._choose_calculator)
        self.pushButton_3.clicked.connect(self._calculate_clicked)

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

    def _choose_calculator(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать изображение",
            "",
            "Python script (*.py);;Все файлы (*)"
        )

        if file_path:  # Если пользователь выбрал файл
            self.calculator.choose_calculator(file_path)


    def _calculate_clicked(self):
        if self.calculator.calculator is None:
            return self.show_warning_message("You didn't choose any scripts for calculating!")
        try:
            self.calculator.update_calculator_script()
            img1 = self.left_drop_image_label.get_image()
            img2 = self.right_drop_image_label.get_image()
            if img1 is None:
                return self.show_warning_message("You didn't choose first file img!")
            if img2 is None:
                return self.show_warning_message("You didn't choose second file img!")
            self.calculator.set_img1(img1)
            self.calculator.set_img2(img2)
            H = self.calculator.calculate_matrix()

            for i in range(3):
                for j in range(3):
                    el = QTableWidgetItem()
                    print(str(H[i][j]))
                    el.setText(str(H[i][j]))
                    self.homography_matrix_table.setItem(i, j+1, el)

            img = self.calculator.calculate_image(H)
            self.homography_fixed_image_label.update_image(img)



        except Exception as e:
            print("While executing script cauth a error: ",e)
            print("Full error:")
            traceback.print_exc()



