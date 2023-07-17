from PyQt5.QtWidgets import QApplication
import sys
from src.client.Client import DatabaseClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = DatabaseClient()
    client.show()
    sys.exit(app.exec_())
