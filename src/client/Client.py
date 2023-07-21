from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout
import requests
from requests.auth import HTTPBasicAuth
import json
from TableWidget import MyTable
from TextEditWidget import TextEdit
import logging


logging.basicConfig(level=logging.DEBUG, filename="client.log", filemode="w",
                    encoding="utf-8", format="%(asctime)s %(levelname)s %(message)s")


class DatabaseClient(QWidget):
    signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.subwindow = None
        self.setWindowTitle("Database Students")
        self.resize(600, 400)
        self.host = "http://localhost:8000/"

        self.__authentification()
        mainLayout = QHBoxLayout()
        self.table = self.__getRequest().json()
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
        editButton.clicked.connect(self.__createSubwindow)
        buttonLayout.addWidget(editButton)

        self.view.signal.connect(self.__clickedRemoveButton)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def __authentification(self):
        response = requests.get(self.host, auth=("user", "pyro127"))
        print(response.status_code)
        print(response.text)

    @pyqtSlot()
    def __clickedSaveButton(self):
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
        self.__postRequest(data)
        self.__sendImage(data["binary_photo"])

    @pyqtSlot()
    def __clickedRemoveButton(self):
        f = open("delete.json")
        data = json.load(f)
        self.__deleteRequest(data)

    def __createSubwindow(self):
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
            self.subwindow.signal.connect(self.__clickedSaveButton)
            self.subwindow.show()

    def __getRequest(self):
        req = requests.get(self.host + "/get-data")
        return req

    def __postRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        req = requests.post(self.host + "/post-data", json=new_data, headers=hdrs)

    def __sendImage(self, image):
        req = requests.post(url=self.host, json={'binary_photo': image})

    def __deleteRequest(self, data):
        req = requests.delete(self.host + "/delete-data", json=data)
        return req
