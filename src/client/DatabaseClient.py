from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QLineEdit, QLabel, QButtonGroup, \
    QRadioButton, QMessageBox
import requests
from requests.auth import HTTPBasicAuth
import base64
from src.client.MyTable import MyTable
from src.client.TextEdit import TextEdit
from src.client.LoginWidget import LoginWidget
import logging
import configparser
import os.path
from cryptography.fernet import Fernet

config = configparser.RawConfigParser()
cur_folder = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(cur_folder, "settings.ini")
config.read(ini_file)
window_title = config.get("section_client", "window_title")
height = config.getint("section_client", "window_height")
width = config.getint("section_client", "window_width")
host = config.get("section_client", "host")
log_level = config.get("section_log", "level")
file = config.get("section_log", "filename")
mode = config.get("section_log", "filemode")
encoding = config.get("section_log", "encoding")
logging.basicConfig(level=logging.DEBUG, filename=file, filemode=mode, encoding=encoding)

secret_path = os.path.join(cur_folder, "secret.enc")
with open(secret_path, "rb") as f:
    secret = f.read()


def encode_password(password, key):
    bytes_password = password.encode('ascii')
    base64_password = base64.b64encode(bytes_password)
    encoded_password = Fernet(key).encrypt(base64_password)
    return encoded_password


class DatabaseClient(QWidget):
    signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.resize(width, height)
        self.host = host
        self.login = LoginWidget()
        self.login.show()
        self.login.signal.connect(self.__authentification)
        self.saveData = {}
        self.sortedData = []
        self.newData = {}
        self.subwindow = None

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
        self.data = {}

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
            if sender.text() == "Only with photo" and record["photo"]:
                newData.append(record)
            elif sender.text() == "Without photo" and record["photo"] == "":
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

    @pyqtSlot()
    def __authentification(self):
        username = self.login.username.text()
        password = self.login.password.text()
        my_password = encode_password(password, secret)
        response = requests.get(self.host, auth=HTTPBasicAuth(username, my_password))
        if response.status_code == 200:
            self.data = self.__getRequest().json()
            self.view = MyTable(self.data)
            self.setLayouts()
            self.show()
        else:
            QMessageBox.critical(
                None,
                "Error",
                "Incorrect username or password"
            )

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
        cells = {"name": "", "year": "", "photo": "", "course": "", "group": ""}
        selected = self.view.selectedItems()
        currentRow = self.view.currentRow()
        if selected and currentRow < len(self.view.data):
            if self.view.data[currentRow]["photo"]:
                path = self.view.data[currentRow]["photo"]
                image_bytes = self.view.data[currentRow]["binary_photo"]
                cells.update({"photo": path, "binary_photo": image_bytes})
            cells["name"] = selected[0].text()
            cells["year"] = selected[1].text()
            cells["course"] = selected[2].text()
            cells["group"] = selected[3].text()
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
