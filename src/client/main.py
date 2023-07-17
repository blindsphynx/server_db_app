from PyQt5.QtWidgets import QApplication
import sys
import json
from src.client.Client import DatabaseClient

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = DatabaseClient()
    client.show()
    # f = open("save.json")
    # data = json.load(f)
    # client.postRequest(data)
    sys.exit(app.exec_())
