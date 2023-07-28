from PyQt5.QtWidgets import QApplication
import sys
from src.client.DatabaseClient import DatabaseClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = DatabaseClient()
    sys.exit(app.exec_())
