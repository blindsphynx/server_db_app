import sys
from random import randint
import requests
import json

from PyQt5 import QtCore
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QVBoxLayout, QPushButton, QWidget, QTextEdit


class TextEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Редактирование записи")
        self.resize(600, 100)
        self.textEdit1 = QTextEdit()
        self.textEdit2 = QTextEdit()
        self.btnPress1 = QPushButton("Сохранить")
        self.btnPress2 = QPushButton("Отмена")

        layout = QVBoxLayout()
        layout.addWidget(self.textEdit1)
        layout.addWidget(self.textEdit2)
        layout.addWidget(self.btnPress1)
        layout.addWidget(self.btnPress2)
        self.setLayout(layout)

        self.btnPress1.clicked.connect(self.btnPress1_Clicked)
        self.btnPress2.clicked.connect(self.btnPress2_Clicked)

    def btnPress1_Clicked(self):
        self.textEdit1.setPlainText("Кнопочка.\nНе понимаю как оно работает")

    def btnPress2_Clicked(self):
        self.textEdit2.setHtml("<font color='green' size='5'><red>отмена\n</font>")


class DatabaseClient(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subwindow = None
        self.mySubwindow = None
        self.setWindowTitle("Database Example")
        self.resize(950, 500)
        self.host = "http://localhost:8000/"

        self.view = QTableWidget()
        self.view.setColumnCount(6)
        self.view.setHorizontalHeaderLabels(["ID", "Name", "Year", "Photo", "Course", "Group"])

        self.model = QSqlTableModel(self)
        self.model.setTable("Students")
        self.showTable()

        self.button = QPushButton("Редактировать", self)
        self.button.clicked.connect(self.createSubwindow)
        self.button.resize(210, 35)
        self.button.move(450, 350)

    def createSubwindow(self):
        if self.subwindow is None:
            self.subwindow = TextEdit()
        self.subwindow.show()

    def showTable(self):
        self.view = QTableWidget()
        self.view.setColumnCount(6)
        self.view.setHorizontalHeaderLabels(["ID", "Name", "Year", "Photo", "Course", "Group"])
        table = self.getRequest().json()
        records = len(table)
        for i in range(records):
            rows = self.view.rowCount()
            self.view.setRowCount(rows + 1)
            for num in range(records):
                primary_key = QTableWidgetItem(str(table[num]["id"]))
                primary_key.setFlags(primary_key.flags() ^ QtCore.Qt.ItemIsEditable)
                self.view.setItem(num, 0, primary_key)
                self.view.setItem(num, 1, QTableWidgetItem(str(table[num]["name"])))
                self.view.setItem(num, 2, QTableWidgetItem(str(table[num]["year"])))
                self.view.setItem(num, 3, QTableWidgetItem(str(table[num]["photo"])))
                self.view.setItem(num, 4, QTableWidgetItem(str(table[num]["course"])))
                self.view.setItem(num, 5, QTableWidgetItem(str(table[num]["group"])))

        self.view.resizeColumnsToContents()
        self.setCentralWidget(self.view)

    def getRequest(self):
        req = requests.get(self.host + "/get-data")
        return req

    def postRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        req = requests.post(self.host + "/post-data", json=new_data, headers=hdrs)
        print(req.headers)


if __name__ == '__main__':
    f = open("file.json")
    data = json.load(f)
    # print("JSON: ", data)
    app = QApplication(sys.argv)
    client = DatabaseClient()
    client.show()
    # client.postRequest(data)
    sys.exit(app.exec_())
