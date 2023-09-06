import configparser
import logging.config
import os.path
import hashlib

import requests
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox
from requests.auth import HTTPBasicAuth

from LoginWidget import LoginWidget
from MyTable import MyTable
from TextEdit import TextEdit


config = configparser.RawConfigParser()
cur_folder = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(cur_folder, "settings.ini")
config.read(ini_file)

logging.config.fileConfig(ini_file)
logger = logging.getLogger("root")

window_title = config.get("section_client", "window_title")
height = config.getint("section_client", "window_height")
width = config.getint("section_client", "window_width")
host = config.get("section_client", "host")
salt = config.get("section_client", "salt")


def encode_password(password):
    salted = password + salt
    hashed = hashlib.md5(salted.encode())
    return hashed.hexdigest()


class DatabaseClient(QWidget):
    signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        # self.resize(width, height)
        self.host = host
        self.data = {}
        self.view = MyTable(self.data)
        self.login = LoginWidget()
        self.login.show()
        self.login.signal.connect(self.__authentification)
        self.saveData = {}
        self.sortedData = []
        self.newData = {}
        self.subwindow = None


    def radioButtonPhoto(self):
        self.sortedData = []
        sender = self.sender()
        for record in self.data:
            if sender.text() == "Only with photo" and record["photo"]:
                self.sortedData.append(record)
            elif sender.text() == "Without photo" and record["photo"] == "":
                self.sortedData.append(record)
            elif sender.text() == "All records":
                self.sortedData = self.data
                break
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
        my_password = encode_password(password)
        response = requests.get(self.host, auth=HTTPBasicAuth(username, my_password))
        if response.status_code == 200:
            self.data = self.__getRequest().json()
            self.show()
            self.login.close()
            self.view.showTable(self.data)
        else:
            QMessageBox.critical(
                None,
                "Error",
                "Incorrect username or password"
            )
            logger.info("Incorrect username or password")

    def newRecord(self):
        self.__createSubwindow()

    @pyqtSlot()
    def __clickedSaveButton(self):
        if self.subwindow.newData:
            if self.subwindow.newData["id"] > len(self.data):
                self.data.append(self.subwindow.newData)
            else:
                for i in range(len(self.data)):
                    if self.data[i]["id"] == self.subwindow.newData["id"]:
                        self.data[i] = self.saveData
                        break
            self.data = self.__postRequest(self.subwindow.newData)
            self.view.showTable(self.data)

    @pyqtSlot()
    def __clickedRemoveButton(self):
        self.data = self.__deleteRequest(self.view.deleteData)
        self.view.showTable(self.data)

    @pyqtSlot()
    def createSubwindow(self):
        cells = {"name": "", "year": "", "photo": "", "course": "", "group": ""}
        selected = self.view.selectedItems()
        self.currentRow = self.view.currentRow()
        if self.currentRow == -1 and self.sender().text() == "New record":
            self.subwindow = TextEdit(cells, len(self.view.data) + 1)
        if selected and self.currentRow < len(self.view.data):
            if self.view.data[self.currentRow]["photo"]:
                path = self.view.data[self.currentRow]["photo"]
                image_bytes = self.view.data[self.currentRow]["binary_photo"]
                cells.update({"photo": path, "binary_photo": image_bytes})
            cells["name"] = selected[0].text()
            cells["year"] = selected[1].text()
            cells["course"] = selected[2].text()
            cells["group"] = selected[3].text()
            self.subwindow = TextEdit(cells, self.currentRow)
        if self.subwindow is not None:
            self.subwindow.signal.connect(self.__clickedSaveButton)

    def __getRequest(self):
        req = requests.get(self.host + "/get-data")
        logger.info("GET request is sent to the server")
        return req

    def __postRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        requests.post(self.host + "/post-data", json=new_data, headers=hdrs)
        logger.info("POST request is sent to the server")
        answer = requests.get(self.host + "/get-data")
        sorted_json = sorted(answer.json(), key=lambda x: x["id"])
        return sorted_json

    def __editDataRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        requests.post(self.host + "/edit-data", json=new_data, headers=hdrs)
        logger.info("POST request is sent to the server")
        answer = requests.get(self.host + "/get-data")
        sorted_json = sorted(answer.json(), key=lambda x: x["id"])
        return sorted_json

    def __deleteRequest(self, data):
        requests.delete(self.host + "/delete-data", json=data)
        logger.info("DELETE request is sent to the server")
        answer = requests.get(self.host + "/get-data")
        return answer.json()
