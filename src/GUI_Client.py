import sys
import requests
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox,
    QTableWidget, QTableWidgetItem,
)


class DatabaseClient(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Example")
        self.resize(850, 400)
        self.connection = QSqlDatabase.addDatabase("QPSQL")
        self.host = "http://localhost:8000/"

        self.view = QTableWidget()
        self.view.setColumnCount(6)
        self.view.setHorizontalHeaderLabels(["ID", "Name", "Year", "Photo", "Course", "Group"])

        self.model = QSqlTableModel(self)
        self.model.setTable("Students")
        if self.createConnection():
            self.showTable()

    def createConnection(self):
        self.connection = QSqlDatabase.addDatabase("QPSQL")
        self.connection.setDatabaseName("postgres1")
        self.connection.setHostName('localhost')
        self.connection.setUserName('user')
        self.connection.setPassword('pyro127')

        if not self.connection.open():
            QMessageBox.critical(
                None,
                "Error!",
                "Unable to connect a database\n\n"
                "Database Error: %s" % self.connection.lastError().databaseText(),
            )
            return False
        return True

    def showTable(self):
        self.view = QTableWidget()
        self.view.setColumnCount(6)
        self.view.setHorizontalHeaderLabels(["ID", "Name", "Year", "Photo", "Course", "Group"])
        table = self.getRequest().json()
        print("returned JSON: ", table)
        for i in range(5):
            # rows = self.view.rowCount()
            # self.view.setRowCount(rows + 1)
            rows = self.view.columnCount()
            self.view.setRowCount(rows - 1)
            for num in range(5):
                # self.view.setItem(rows, num, QTableWidgetItem(str(table.value(num))))
                self.view.setItem(rows, num, QTableWidgetItem(str(table[num]["id"])))
                self.view.setItem(rows, num, QTableWidgetItem(str(table[num]["name"])))
                # self.view.setItem(rows, num, QTableWidgetItem(str(table[num]["year"])))
                # self.view.setItem(rows, num, QTableWidgetItem(str(table[num]["photo"])))
                # self.view.setItem(rows, num, QTableWidgetItem(str(table[num]["course"])))
                # self.view.setItem(rows, num, QTableWidgetItem(str(table[num]["group"])))
                # print(table[num])

        self.view.resizeColumnsToContents()
        self.setCentralWidget(self.view)

    def getRequest(self):
        req = requests.get(self.host + "/get-data")
        # print(req.text)
        return req

    def postRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        req = requests.post(self.host + "/post-data", json=new_data, headers=hdrs)
        print(req.headers)
        print(req.text)


if __name__ == '__main__':
    # f = open("src/file.json")
    # data = json.load(f)
    # print("JSON: ", data)
    app = QApplication(sys.argv)
    client = DatabaseClient()
    client.show()

    # client.postRequest(data)
    # client.getRequest()
    sys.exit(app.exec_())
