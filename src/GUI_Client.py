import sys
import requests
import json
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, \
    QVBoxLayout, QPushButton, QWidget, QHBoxLayout


class TextEdit(QWidget):
    def __init__(self, cells, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Edit record")
        self.resize(600, 100)
        self.editField1 = QLineEdit(self)
        self.editField2 = QLineEdit(self)
        self.editField3 = QLineEdit(self)
        self.editField4 = QLineEdit(self)

        self.btnPress1 = QPushButton("Save")
        self.btnPress2 = QPushButton("Cancel")
        self.nameLabel = QLabel(self)
        self.yearLabel = QLabel(self)
        self.courseLabel = QLabel(self)
        self.groupLabel = QLabel(self)
        self.cells = cells

        if self.cells:
            self.setValues()
        layout = QVBoxLayout()
        layout.addWidget(self.editField1)
        layout.addWidget(self.editField2)
        layout.addWidget(self.editField3)
        layout.addWidget(self.editField4)
        layout.addWidget(self.btnPress1)
        layout.addWidget(self.btnPress2)
        self.setLayout(layout)
        self.btnPress1.clicked.connect(self.btnPress1_Clicked)
        self.btnPress2.clicked.connect(self.btnPress2_Clicked)

    def setValues(self):
        # add names of the fields
        self.editField1.setText(self.cells["name"])
        self.editField2.setText(self.cells["year"])
        # upload image
        self.editField3.setText(self.cells["course"])
        self.editField4.setText(self.cells["group"])

    def insert(self, cells):
        self.cells = cells
        print("cells: ", cells)

    def btnPress1_Clicked(self):
        if self.editField1.text():
            print("New data: " + self.editField1.text())
        else:
            print("Error: required argument 'name'")
        # save data to json and return to table

    def btnPress2_Clicked(self):
        print("Canceled: " + self.editField2.text())


class MyTable(QTableWidget):
    def __init__(self, tableData, parent=None):
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["ID", "Name", "Year", "Photo", "Course", "Group"])
        self.data = tableData

    def addNewRow(self):
        rowCount = self.rowCount()
        self.insertRow(rowCount)

    def removeOneRow(self):
        # removes the last column
        if self.rowCount() > 0:
            self.removeRow(self.rowCount() - 1)

    def showTable(self):
        records = len(self.data)
        for i in range(records):
            rows = self.rowCount()
            self.setRowCount(rows + 1)
            for num in range(records):
                primary_key = QTableWidgetItem(str(self.data[num]["id"]))
                primary_key.setFlags(primary_key.flags() ^ QtCore.Qt.ItemIsEditable)
                self.setItem(num, 0, primary_key)
                self.setItem(num, 1, QTableWidgetItem(str(self.data[num]["name"])))
                self.setItem(num, 2, QTableWidgetItem(str(self.data[num]["year"])))
                self.setItem(num, 3, QTableWidgetItem(str(self.data[num]["photo"])))
                self.setItem(num, 4, QTableWidgetItem(str(self.data[num]["course"])))
                self.setItem(num, 5, QTableWidgetItem(str(self.data[num]["group"])))
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
        fields = ["id", "name", "year", "photo", "course", "group"]
        selected = self.view.selectedItems()
        for i in range(len(selected)):
            cells.update({fields[i]: self.view.selectedItems()[i].text()})

        if self.subwindow is None:
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
