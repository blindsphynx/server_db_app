from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QLineEdit, QMainWindow
import requests
import json
from TableWidget import MyTable
from TextEditWidget import TextEdit


class DatabaseClient(QWidget):
    signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.subwindow = None
        self.setWindowTitle("Database Students")
        self.resize(1100, 500)
        self.host = "http://localhost:8000/"

        mainLayout = QHBoxLayout()
        self.table = self.getRequest().json()
        self.view = MyTable(self.table)
        mainLayout.addWidget(self.view)

        self.setLayout(mainLayout)
        buttonLayout = QVBoxLayout()

        newButton = QPushButton("New record")
        newButton.clicked.connect(self.view.addNewRow)
        buttonLayout.addWidget(newButton)

        removeButton = QPushButton("Remove")
        removeButton.clicked.connect(self.view.removeOneRow)
        buttonLayout.addWidget(removeButton)

        editButton = QPushButton("Edit")
        editButton.clicked.connect(self.createSubwindow)
        buttonLayout.addWidget(editButton)

        self.view.signal.connect(self.clickedRemoveButton)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    @pyqtSlot()
    def clickedSaveButton(self):
        f = open("save.json")
        data = json.load(f)
        for i in range(len(self.table)):
            if data["id"] > len(self.table):
                self.table.append(data)
                break
            if self.table[i]["id"] == data["id"]:
                self.table[i] = data
            else:
                continue
        self.view.showTable(self.table)
        self.postRequest(data)
        self.sendImage(data["binary_photo"])

    @pyqtSlot()
    def clickedRemoveButton(self):
        f = open("delete.json")
        data = json.load(f)
        self.deleteRequest(data)

    def createSubwindow(self):
        cells = {}
        fields = ["name", "year", "course", "group"]
        selected = self.view.selectedItems()
        currentRow = self.view.currentRow()
        if selected:
            if currentRow < len(self.view.data):
                if self.view.data[currentRow]["photo"]:
                    path = self.view.data[currentRow]["photo"]
                else:
                    path = ""
                for i in range(len(selected)):
                    cells.update({fields[i]: self.view.selectedItems()[i].text()})
                    cells.update({"photo": path})
            else:
                cells = {"name": "", "year": "", "photo": "", "course": "", "group": ""}
            self.subwindow = TextEdit(cells, currentRow)
            self.subwindow.signal.connect(self.clickedSaveButton)
            self.subwindow.show()

    def getRequest(self):
        req = requests.get(self.host + "/get-data")
        return req

    def postRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        req = requests.post(self.host + "/post-data", json=new_data, headers=hdrs)

    def sendImage(self, image):
        req = requests.post(url=self.host, json={'binary_photo': image})

    def deleteRequest(self, data):
        req = requests.delete(self.host + "/delete-data", json=data)
        return req
