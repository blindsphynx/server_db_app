from PyQt5.QtWidgets import QApplication
import sys
from src.client.Client import DatabaseClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = DatabaseClient()
    client.show()
    # client.postRequest(data)
    sys.exit(app.exec_())
