import json

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout
from TextEditWidget import TextEdit
import requests
from TableWidget import MyTable


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

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    @pyqtSlot()
    def clickedButton(self):
        print("click!")
        f = open("save.json")
        data = json.load(f)
        for i in range(len(self.table)):
            if self.table[i]["id"] == data["id"]:
                self.table[i] = data
                break
            else:
                self.table.append(data)
                break
        self.view.showTable(self.table)
        self.postRequest(data)

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
            self.subwindow.signal.connect(self.clickedButton)
            self.subwindow.show()

    def getRequest(self):
        req = requests.get(self.host + "/get-data")
        return req

    def postRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        req = requests.post(self.host + "/post-data", json=new_data, headers=hdrs)
        # print(req.headers)
