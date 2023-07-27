from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QLineEdit, QLabel, QButtonGroup, \
    QRadioButton
import requests
from requests.auth import HTTPBasicAuth
import json
import base64
from MyTable import MyTable
from TextEdit import TextEdit
import logging
import configparser
from cryptography.fernet import Fernet

config = configparser.ConfigParser()
config.read('settings.ini')
username = config.get('section_auth', 'username')
my_password = config.get('section_auth', 'password')
# key = config.get('section_auth', 'key')
log_level = config.get('section_log', 'level')
file = config.get('section_log', 'filename')
mode = config.get('section_log', 'filemode')
encoding = config.get('section_log', 'encoding')
logging.basicConfig(level=logging.DEBUG, filename="../client/client.log", filemode="w",
                    encoding="utf-8", format="%(asctime)s %(levelname)s %(message)s")


def encode_password(password, key):
    bytes_password = password.encode('ascii')
    base64_password = base64.b64encode(bytes_password)
    encoded_password = Fernet(key).encrypt(base64_password)
    return encoded_password


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
        self.sortedData = []
        self.view = MyTable(self.data)
        self.saveData = {}

        self.mainLayout = QHBoxLayout()
        self.commonLayout = QVBoxLayout()
        self.filter_layout = QHBoxLayout()
        self.radioButtonLayout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.photoFilterButton = QRadioButton()
        self.photoFilterButton2 = QRadioButton()
        self.newButton = QPushButton("New record")
        self.removeButton = QPushButton("Remove")
        self.editButton = QPushButton("Edit")
        self.newData = {}

        self.setLayouts()

    def setLayouts(self):
        label = QLabel("Search: ")
        self.search_bar.textChanged.connect(self.findSubstring)
        self.filter_layout.addWidget(label)
        self.filter_layout.addWidget(self.search_bar)
        self.commonLayout.addLayout(self.filter_layout)
        self.commonLayout.addWidget(self.view)

        button_group = QButtonGroup(self)
        button_group.setExclusive(True)

        self.photoFilterButton.setText("Only with photo")
        self.photoFilterButton.toggled.connect(self.radioButtonPhoto)
        self.photoFilterButton2.setText("Without photo")
        self.photoFilterButton2.toggled.connect(self.radioButtonPhoto)
        button_group.addButton(self.photoFilterButton)
        self.commonLayout.addWidget(self.photoFilterButton)
        button_group.addButton(self.photoFilterButton2)
        self.commonLayout.addWidget(self.photoFilterButton2)

        self.setLayout(self.mainLayout)
        buttonLayout = QVBoxLayout()

        self.newButton.clicked.connect(self.view.addNewRow)
        buttonLayout.addWidget(self.newButton)
        self.removeButton.clicked.connect(self.view.removeOneRow)
        buttonLayout.addWidget(self.removeButton)
        self.editButton.clicked.connect(self.__createSubwindow)
        buttonLayout.addWidget(self.editButton)

        self.view.signal.connect(self.__clickedRemoveButton)
        self.mainLayout.addLayout(self.commonLayout)
        self.mainLayout.addLayout(buttonLayout)
        self.setLayout(self.mainLayout)

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
        self.sortedData = newData
        self.view.showTable(self.sortedData)

    def findSubstring(self, filter_text):
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
        # self.form = LoginForm()
        # self.form.show()
        my_key = b'yRIKdydLGHRMmJ-gFdgnhafhd4qi_w8BU2jHsmLP-LM='
        password = encode_password(my_password, my_key)
        response = requests.get(self.host, auth=HTTPBasicAuth(username, password))
        print(response.request.headers)

    @pyqtSlot()
    def __clickedSaveButton(self):
        self.saveData = self.subwindow.newData
        if self.saveData["id"] > len(self.data):
            self.data.append(self.saveData)
        else:
            for i in range(len(self.data)):
                if self.data[i]["id"] == self.saveData["id"]:
                    self.data[i] = self.saveData
                    break
        self.view.showTable(self.data)
        self.__postRequest(self.saveData)

    @pyqtSlot()
    def __clickedRemoveButton(self):
        self.__deleteRequest(self.view.deleteData)

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
