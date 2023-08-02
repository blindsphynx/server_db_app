from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTableWidgetItem, QLabel, QTableWidget, QAbstractItemView
from operator import xor
import base64


def getImageLabel(img):
    image = base64.b64decode(img)
    try:
        imglabel = QLabel(" ")
        imglabel.setScaledContents(True)
        pixmap = QPixmap()
        pixmap.loadFromData(image, 'jpg')
        imglabel.setPixmap(pixmap)
        return imglabel
    except Exception as err:
        print(err)


class MyTable(QTableWidget):
    signal = pyqtSignal()

    def __init__(self, tableData, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Name", "Year", "Photo", "Course", "Group"])
        self.data = tableData
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setMinimumHeight(500)
        self.setMinimumWidth(700)
        self.showTable(self.data)
        self.deleteData = {}

    def addNewRow(self):
        rowCount = self.rowCount()
        self.insertRow(self.rowCount())
        for i in range(self.columnCount() - 1):
            self.setItem(rowCount, i, QTableWidgetItem(""))

    @pyqtSlot()
    def removeOneRow(self):
        selected = self.selectedItems()
        if selected:
            if self.currentRow() < len(self.data):
                data = self.data[self.currentRow()]
                self.deleteData = {"name": data["name"]}
                self.signal.emit()
            self.removeRow(self.currentRow())

    def showTable(self, newData):
        self.clearContents()
        self.data = newData
        records = len(self.data)
        for i in range(records):
            self.setRowCount(records)
            for num in range(records):
                name = QTableWidgetItem(str(self.data[num]["name"]))
                name.setFlags(xor(name.flags(), QtCore.Qt.ItemIsEditable))
                year = QTableWidgetItem(str(self.data[num]["year"]))
                year.setFlags(xor(year.flags(), QtCore.Qt.ItemIsEditable))
                course = QTableWidgetItem(str(self.data[num]["course"]))
                course.setFlags(xor(course.flags(), QtCore.Qt.ItemIsEditable))
                group = QTableWidgetItem(str(self.data[num]["group"]))
                group.setFlags(xor(group.flags(), QtCore.Qt.ItemIsEditable))
                self.setItem(num, 0, name)
                self.setItem(num, 1, year)
                self.setItem(num, 3, course)
                self.setItem(num, 4, group)
                if self.data[num]["photo"]:
                    item = getImageLabel(self.data[num]["binary_photo"])
                    self.setCellWidget(num, 2, item)
                else:
                    item = QTableWidgetItem()
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.setItem(num, 2, item)
                self.setRowHeight(num, 150)
        self.setColumnWidth(0, 300)
