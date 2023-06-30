from PyQt5.QtWidgets import QApplication, QDialog
import requests
import sys


class Client(QDialog):
    def __init__(self):
        super().__init__()
        self.host = "http://localhost:8000/"
        print("Client was created")

    def getRequest(self):
        data = requests.get(self.host + "/get-data")
        # print(data.headers)
        print(data.text)

    def postRequest(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.getRequest()
    sys.exit(client.exec_())
