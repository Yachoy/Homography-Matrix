from PySide6.QtWidgets import QTableWidget, QApplication
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QKeySequence


class TableWidgetCopy(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def copy(self):
        """Копирует выделенные ячейки в буфер обмена в формате CSV."""
        selection = self.selectedRanges()
        if not selection:
            selection = [self.visualItemRect(self.item(0, 0))] if self.item(0, 0) is not None else []

        if selection:
            copied_text = ""
            for sel_range in selection:
                for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                    for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                        item = self.item(row, col)
                        if item:
                            copied_text += item.text()
                        if col < sel_range.rightColumn():
                            copied_text += "\t"
                    copied_text += "\n"
                copied_text += "\n"

            mime_data = QMimeData()
            mime_data.setText(copied_text)
            QApplication.instance().clipboard().setMimeData(mime_data)

    def paste(self):
        """Вставляет данные из буфера обмена в таблицу, начиная с текущей ячейки."""
        mime_data = QApplication.instance().clipboard().mimeData()
        if mime_data and mime_data.hasText():
            text = mime_data.text()
            rows = text.strip().split('\n\n')  # Разделяем на блоки строк

            current_row = self.currentRow()
            current_col = self.currentColumn()

            for block in rows:  # Проходим по каждому блоку
                lines = block.strip().split('\n')
                for row_idx, line in enumerate(lines):
                    cells = line.split('\t')
                    for col_idx, cell in enumerate(cells):
                        row = current_row + row_idx
                        col = current_col + col_idx

                        # Проверяем границы таблицы
                        if row < self.rowCount() and col < self.columnCount():
                            item = QTableWidgetItem(cell)
                            self.setItem(row, col, item)
                        else:
                            # Если вышли за границы, увеличиваем размер таблицы
                            while row >= self.rowCount():
                                self.insertRow(self.rowCount())
                            while col >= self.columnCount():
                                self.insertColumn(self.columnCount())
                            item = QTableWidgetItem(cell)
                            self.setItem(row, col, item)

    def keyPressEvent(self, event):
        """Обрабатывает нажатия клавиш Ctrl+C и Ctrl+V."""
        if event.matches(QKeySequence.Copy):
            self.copy()
        elif event.matches(QKeySequence.Paste):
            self.paste()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    table = TableWidgetCopy(5, 3)
    table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

    for row in range(5):
        for col in range(3):
            item = QTableWidgetItem(f"Row {row + 1}, Col {col + 1}")
            table.setItem(row, col, item)

    table.show()
    app.exec()