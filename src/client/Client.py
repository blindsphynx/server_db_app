from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout
from TextEditWidget import TextEdit
import requests
from TableWidget import MyTable


class DatabaseClient(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subwindow = None
        self.setWindowTitle("Database Students")
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
        fields = ["name", "year", "course", "group"]
        selected = self.view.selectedItems()
        if self.view.data[self.view.currentRow()]["photo"]:
            path = self.view.data[self.view.currentRow()]["photo"]
        else:
            path = ""
        if selected:
            for i in range(len(selected)):
                cells.update({fields[i]: self.view.selectedItems()[i].text()})
            cells.update({"photo": path})
        else:
            for i in range(len(fields)):
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
