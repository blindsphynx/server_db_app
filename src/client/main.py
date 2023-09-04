from PyQt5.QtWidgets import QApplication
import sys
from DatabaseClient import DatabaseClient, Ui_DatabaseClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Ui_DatabaseClient()
    dbClient = DatabaseClient()
    client.setupUi(dbClient)
    sys.exit(app.exec_())
