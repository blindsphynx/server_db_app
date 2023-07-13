import sys
import requests
import json

from PyQt5 import QtGui
from PyQt5.QtCore import QDir, QFile, QIODevice, QFileInfo
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, \
    QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QAbstractItemView, QMessageBox, QFileDialog


class TextEdit(QWidget):
    def __init__(self, cells, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit record")
        self.resize(900, 400)
        self.editField1 = QLineEdit(self)
        self.editField2 = QLineEdit(self)
        self.editField3 = QLineEdit(self)
        self.editField4 = QLineEdit(self)
        self.saveButton = QPushButton("Save")
        self.cancelButton = QPushButton("Cancel")
        self.cells = cells

        self.setValues()
        mainLayout = QVBoxLayout()
        labelsLayout = QVBoxLayout()
        fieldsLayout = QVBoxLayout()
        commonLayout = QHBoxLayout()
        buttonsLayout = QHBoxLayout()

        label1 = QLabel("Name:")
        label2 = QLabel("Year:")
        label3 = QLabel("Course:")
        label4 = QLabel("Group:")

        labelsLayout.addWidget(label1)
        fieldsLayout.addWidget(self.editField1)
        labelsLayout.addWidget(label2)
        fieldsLayout.addWidget(self.editField2)
        labelsLayout.addWidget(label3)
        fieldsLayout.addWidget(self.editField3)
        labelsLayout.addWidget(label4)
        fieldsLayout.addWidget(self.editField4)

        buttonsLayout.addWidget(self.saveButton)
        buttonsLayout.addWidget(self.cancelButton)

        commonLayout.addLayout(labelsLayout)
        commonLayout.addLayout(fieldsLayout)
        mainLayout.addLayout(commonLayout)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)

    def setValues(self):
        self.editField1.setAccessibleName("name: ")
        self.editField1.setText(self.cells["name"])
        self.editField2.setText(self.cells["year"])
        # upload image
        self.editField3.setText(self.cells["course"])
        self.editField4.setText(self.cells["group"])

    def saveButtonClicked(self):
        if self.editField1.text():
            newData = {"name": self.editField1.text(), "year": self.editField2.text(),
                       "course": self.editField3.text(), "group": self.editField4.text()}
            json_object = json.dumps(newData, indent=4)
            with open("sample.json", "w") as outfile:
                outfile.write(json_object)

            self.infoMessageBox(title="Saving", message="Data was saved")
        else:
            QMessageBox.critical(
                None,
                "Error while saving",
                "Required field 'name'"
            )

    def cancelButtonClicked(self):
        self.editField1.setText(self.cells["name"])
        self.editField2.setText(self.cells["year"])
        self.editField3.setText(self.cells["course"])
        self.editField4.setText(self.cells["group"])
        self.infoMessageBox(title="Cancel", message="Changes were canceled")

    def infoMessageBox(self, title, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.buttonClicked.connect(msgBox.close)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print("cancel OK clicked")


class ImageWidget(QWidget):
    def __init__(self, imagePath, parent):
        super(ImageWidget, self).__init__(parent)
        self.picture = QtGui.QPixmap(imagePath)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.picture)


class MyTable(QTableWidget):
    def __init__(self, tableData, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Name", "Year", "Photo", "Course", "Group"])
        self.data = tableData
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def addNewRow(self):
        rowCount = self.rowCount()
        self.insertRow(rowCount)

    def removeOneRow(self):
        selected = self.selectedItems()
        if selected:
            # вынести запись в файл в отдельную функ
            # и тут записывать тоже что было удалено
            self.removeRow(self.currentRow())

    def setImage(self, imagePath):
        image = QLabel()
        image.setText("")
        image.setScaledContents(True)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(imagePath)
        image.setPixmap(pixmap)
        return image

    def showTable(self):
        records = len(self.data)
        for i in range(records):
            rows = self.rowCount()
            self.setRowCount(rows + 1)
            for num in range(records):
                self.setItem(num, 0, QTableWidgetItem(str(self.data[num]["name"])))
                self.setItem(num, 1, QTableWidgetItem(str(self.data[num]["year"])))
                if num == 0:
                    item = self.setImage("kitty.jpg")
                    self.setItem(num, 2, QTableWidgetItem(item))
                else:
                    self.setItem(num, 2, QTableWidgetItem(str(self.data[num]["photo"])))
                self.setItem(num, 3, QTableWidgetItem(str(self.data[num]["course"])))
                self.setItem(num, 4, QTableWidgetItem(str(self.data[num]["group"])))
        self.resizeColumnsToContents()


class DatabaseClient(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subwindow = None
        self.setWindowTitle("Database Example")
        self.resize(1100, 500)
        self.host = "http://localhost:8000/"

        mainLayout = QHBoxLayout()
        table = self.getRequest().json()
        self.view = MyTable(table)
        mainLayout.addWidget(self.view)

        self.setLayout(mainLayout)
        buttonLayout = QVBoxLayout()
        self.view.showTable()

        newButton = QPushButton("New record")
        newButton.clicked.connect(self.view.addNewRow)
        buttonLayout.addWidget(newButton)

        removeButton = QPushButton("Remove")
        removeButton.clicked.connect(self.view.removeOneRow)
        buttonLayout.addWidget(removeButton)

        editButton = QPushButton("Edit")
        editButton.clicked.connect(self.createSubwindow)
        buttonLayout.addWidget(editButton)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def createSubwindow(self):
        cells = {}
        fields = ["name", "year", "photo", "course", "group"]
        selected = self.view.selectedItems()
        if selected:
            for i in range(len(selected)):
                cells.update({fields[i]: self.view.selectedItems()[i].text()})
        else:
            for i in range(5):
                cells.update({fields[i]: ""})
        self.subwindow = TextEdit(cells)
        self.subwindow.show()

    def getRequest(self):
        req = requests.get(self.host + "/get-data")
        return req

    def postRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        req = requests.post(self.host + "/post-data", json=new_data, headers=hdrs)
        # print(req.headers)


if __name__ == '__main__':
    f = open("file.json")
    data = json.load(f)
    app = QApplication(sys.argv)
    client = DatabaseClient()
    client.show()
    # client.postRequest(data)
    sys.exit(app.exec_())
