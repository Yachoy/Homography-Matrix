from tkinter import Frame

from PySide6.QtWidgets import QTableWidget, QApplication
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QKeySequence

from PySide6.QtWidgets import QTableWidget, QApplication
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QKeySequence


class TableWidgetCopy(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def copy(self):
        """Копирует выделенные ячейки в буфер обмена в формате CSV."""

        selection = self.selectedRanges()
        if not selection:  # Если ничего не выделено, копируем всю таблицу
            selection = [self.visualItemRect(self.item(0, 0))] if self.item(0,
                                                                            0) is not None else []  # Проверка на пустую таблицу

        if selection:
            copied_text = ""

            for sel_range in selection:  # Изменено имя переменной
                for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                    for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                        item = self.item(row, col)
                        if item:
                            copied_text += item.text()
                        if col < sel_range.rightColumn():  # Добавляем разделитель между ячейками
                            copied_text += "\t"
                    copied_text += "\n"  # Переход на новую строку после каждой строки таблицы
                copied_text += "\n"  # Добавляем пустую строку между выделенными областями

            mime_data = QMimeData()
            mime_data.setText(copied_text)
            QApplication.instance().clipboard().setMimeData(mime_data)

    def paste(self):
        mime_data = QApplication.instance().clipboard().mimeData()
        if mime_data.hasText():
            text = mime_data.text()
            rows = text.strip().split('\n')
            current_row = self.currentRow()
            current_col = self.currentColumn()

            for i, row_text in enumerate(rows):
                cols = row_text.split('\t')
                for j, col_text in enumerate(cols):
                    row = current_row + i
                    col = current_col + j

                    if row < self.rowCount() and col < self.columnCount():
                        item = QTableWidgetItem(col_text)
                        self.setItem(row, col, item)
                    else:
                        # Pum pum pum...
                        pass  # Here, we choose to ignore the extra data (you can modify it to your need).
                        break

    def keyPressEvent(self, event):
        """Обрабатывает нажатия клавиш, в частности Ctrl+C для копирования."""
        if event.matches(QKeySequence.Copy):  # Проверяем, что нажата комбинация Ctrl+C
            self.copy()
        else:
            super().keyPressEvent(event)  # Передаем остальные события родительскому классу


if __name__ == "__main__":
    app = QApplication([])
    table = TableWidgetCopy(5, 3)  # Создаем таблицу 5x3
    table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

    # Заполняем таблицу данными (необязательно для теста копирования пустой таблицы)
    for row in range(5):
        for col in range(3):
            item = QTableWidgetItem(f"Row {row + 1}, Col {col + 1}")
            table.setItem(row, col, item)

    table.show()
    app.exec()