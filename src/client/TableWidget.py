from PyQt5.QtCore import Qt, QDir, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QStandardItemModel
from PyQt5.QtWidgets import QTableWidgetItem, QLabel, QTableWidget, QAbstractItemView
import json
import os


def getImageLabel(path):
    path = os.path.basename(path)
    print(path)
    with open(QDir.currentPath() + "/client_pictures/" + path, "rb") as image:
        file = image.read()
        b = bytearray(file)
    try:
        imglabel = QLabel(" ")
        imglabel.setScaledContents(True)
        pixmap = QPixmap()
        pixmap.loadFromData(b, 'jpg')
        imglabel.setPixmap(pixmap)
        imglabel.setFixedWidth(150)
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
        self.showTable(self.data)

    def addNewRow(self):
        rowCount = self.rowCount()
        self.insertRow(rowCount)
        self.setItem(rowCount, 0, QTableWidgetItem(" "))

    @pyqtSlot()
    def removeOneRow(self):
        selected = self.selectedItems()
        if selected:
            if self.currentRow() < len(self.data):
                data = self.data[self.currentRow()]
                newData = {"name": data["name"], "year": data["year"],
                           "photo": data["photo"], "course": data["course"],
                           "group": data["group"]}
                json_object = json.dumps(newData, indent=4)
                with open("delete.json", "w") as outfile:
                    outfile.write(json_object)
                self.signal.emit()
                print("remove signal")
            self.removeRow(self.currentRow())

    def showTable(self, newData):
        self.data = newData
        records = len(self.data)
        for i in range(records):
            self.setRowCount(records)
            for num in range(records):
                self.setItem(num, 0, QTableWidgetItem(str(self.data[num]["name"])))
                self.setItem(num, 1, QTableWidgetItem(str(self.data[num]["year"])))
                if self.data[num]["photo"]:
                    item = getImageLabel(self.data[num]["photo"])
                    self.setCellWidget(num, 2, item)
                else:
                    image = QTableWidgetItem()
                    image.setFlags(Qt.ItemIsSelectable)
                    self.setItem(num, 2, image)
                self.setItem(num, 3, QTableWidgetItem(str(self.data[num]["course"])))
                self.setItem(num, 4, QTableWidgetItem(str(self.data[num]["group"])))
        self.resizeColumnsToContents()
