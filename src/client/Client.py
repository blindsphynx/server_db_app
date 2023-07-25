from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QLineEdit, QLabel, QCheckBox, QButtonGroup, \
    QRadioButton
import requests
from requests.auth import HTTPBasicAuth
import json
from TableWidget import MyTable
from TextEditWidget import TextEdit
import logging
import configparser


config = configparser.ConfigParser()
config.read('settings.ini')
log_level = config.get('section_log', 'level')
file = config.get('section_log', 'filename')
mode = config.get('section_log', 'filemode')
encoding = config.get('section_log', 'encoding')
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

        self.data = self.__getRequest().json()
        self.view = MyTable(self.data)

        self.mainLayout = QHBoxLayout()
        self.commonLayout = QVBoxLayout()
        self.filter_layout = QHBoxLayout()
        self.radioButtonLayout = QHBoxLayout()
        self.sortByPhoto = QVBoxLayout()
        self.sortByAlpha = QVBoxLayout()
        self.search_bar = QLineEdit()
        self.setLayouts()

    def setLayouts(self):
        label = QLabel("Search: ")
        self.search_bar.textChanged.connect(self.filter)
        self.filter_layout.addWidget(label)
        self.filter_layout.addWidget(self.search_bar)
        self.commonLayout.addLayout(self.filter_layout)
        self.commonLayout.addWidget(self.view)

        button_group1 = QButtonGroup(self)
        button_group1.setExclusive(True)
        button_group2 = QButtonGroup(self)
        button_group2.setExclusive(True)
        self.checkbox1 = QRadioButton()
        self.checkbox1.setText("Only with photo")
        self.checkbox1.toggled.connect(self.radioButtonPhoto)
        self.checkbox2 = QRadioButton()
        self.checkbox2.setText("Without photo")
        self.checkbox2.toggled.connect(self.radioButtonPhoto)
        button_group1.addButton(self.checkbox1)
        self.sortByPhoto.addWidget(self.checkbox1)
        button_group1.addButton(self.checkbox2)
        self.sortByPhoto.addWidget(self.checkbox2)

        self.checkbox3 = QRadioButton()
        self.checkbox3.setText("In alphabetical order")
        self.checkbox3.toggled.connect(self.radioButtonAlpha)
        self.checkbox4 = QRadioButton()
        self.checkbox4.setText("In reverse alphabetical order")
        self.checkbox4.toggled.connect(self.radioButtonAlpha)
        button_group2.addButton(self.checkbox3)
        self.sortByAlpha.addWidget(self.checkbox3)
        button_group2.addButton(self.checkbox4)
        self.sortByAlpha.addWidget(self.checkbox4)
        self.radioButtonLayout.addLayout(self.sortByPhoto)
        self.radioButtonLayout.addLayout(self.sortByAlpha)
        self.commonLayout.addLayout(self.radioButtonLayout)

        self.setLayout(self.mainLayout)
        buttonLayout = QVBoxLayout()

        self.newButton = QPushButton("New record")
        self.newButton.clicked.connect(self.view.addNewRow)
        buttonLayout.addWidget(self.newButton)

        self.removeButton = QPushButton("Remove")
        self.removeButton.clicked.connect(self.view.removeOneRow)
        buttonLayout.addWidget(self.removeButton)

        self.editButton = QPushButton("Edit")
        self.editButton.clicked.connect(self.__createSubwindow)
        buttonLayout.addWidget(self.editButton)

        self.view.signal.connect(self.__clickedRemoveButton)
        self.mainLayout.addLayout(self.commonLayout)
        self.mainLayout.addLayout(buttonLayout)
        self.setLayout(self.mainLayout)

    def radioButtonAlpha(self):
        sender = self.sender()
        newData = []
        for record in self.data:
            newData.append(record)
        if sender.text() == "In alphabetical order":
            newData = sorted(newData, key=lambda x: x['name'])
        else:
            newData = sorted(newData, key=lambda x: x['name'], reverse=True)
        self.view.showTable(newData)

    def radioButtonPhoto(self):
        sender = self.sender()
        newData = []
        for record in self.data:
            if sender.text() == "Only with photo":
                if record["photo"]:
                    newData.append(record)
            else:
                if record["photo"] == "":
                    newData.append(record)
        self.view.showTable(newData)

    def filter(self, filter_text):
        for i in range(self.view.rowCount()):
            for j in range(self.view.columnCount()):
                if j == 2:
                    continue
                item = self.view.item(i, j)
                match = filter_text.lower() not in item.text().lower()
                self.view.setRowHidden(i, match)
                if not match:
                    break

    def __authentification(self):
        response = requests.get(self.host, auth=("user", "pyro127"))
        # print(response.status_code)
        # print(response.text)

    @pyqtSlot()
    def __clickedSaveButton(self):
        f = open("save.json")
        data = json.load(f)
        for i in range(len(self.data)):
            if data["id"] > len(self.data):
                self.data.append(data)
                break
            if self.data[i]["id"] == data["id"]:
                self.data[i] = data
            else:
                continue
        self.view.showTable(self.data)
        self.__postRequest(data)

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
                    image_bytes = self.view.data[currentRow]["binary_photo"]
                    cells.update({"photo": path, "binary_photo": image_bytes})
                else:
                    path = ""
                    cells.update({"photo": path})
                for i in range(len(selected)):
                    cells.update({fields[i]: self.view.selectedItems()[i].text()})
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

    def __deleteRequest(self, data):
        req = requests.delete(self.host + "/delete-data", json=data)
        return req
