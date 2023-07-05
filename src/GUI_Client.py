import sys
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox,
    QTableWidget, QTableWidgetItem,
)


class Database(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Example")
        self.resize(750, 450)
        self.connection = QSqlDatabase.addDatabase("QPSQL")

        self.view = QTableWidget()
        self.view.setColumnCount(6)
        self.view.setHorizontalHeaderLabels(["ID", "Name", "Year", "Photo", "Course", "Group"])
        query = QSqlQuery("SELECT * FROM students")
        while query.next():
            rows = self.view.rowCount()
            self.view.setRowCount(rows + 1)
            self.view.setItem(rows, 0, QTableWidgetItem(query.value(0)))
            self.view.setItem(rows, 1, QTableWidgetItem(query.value(1)))
            self.view.setItem(rows, 2, QTableWidgetItem(query.value(2)))
            self.view.setItem(rows, 3, QTableWidgetItem(query.value(3)))
            self.view.setItem(rows, 4, QTableWidgetItem(query.value(4)))
            self.view.setItem(rows, 5, QTableWidgetItem(query.value(5)))
        self.model = QSqlTableModel(self)
        self.model.setTable("Students")
        if self.createConnection():
            self.showTable()

        self.view.resizeColumnsToContents()
        self.setCentralWidget(self.view)

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
        print("[INFO] PostgreSQL connection established")
        return True

    def showTable(self):
        self.view = QTableWidget()
        self.view.setColumnCount(6)
        self.view.setHorizontalHeaderLabels(["ID", "Name", "Year", "Photo", "Course", "Group"])
        query = QSqlQuery("SELECT * FROM students")

        while query.next():
            rows = self.view.rowCount()
            self.view.setRowCount(rows + 1)
            self.view.setItem(rows, 0, QTableWidgetItem(str(query.value(0))))
            self.view.setItem(rows, 1, QTableWidgetItem(query.value(1)))
            self.view.setItem(rows, 2, QTableWidgetItem(str(query.value(2))))
            self.view.setItem(rows, 3, QTableWidgetItem(query.value(3)))
            self.view.setItem(rows, 4, QTableWidgetItem(str(query.value(4))))
            self.view.setItem(rows, 5, QTableWidgetItem(str(query.value(5))))
        self.view.resizeColumnsToContents()
        self.setCentralWidget(self.view)


app = QApplication(sys.argv)
win = Database()
win.show()
sys.exit(app.exec_())
