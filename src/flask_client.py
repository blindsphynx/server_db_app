from PyQt5.QtWidgets import QApplication, QDialog
import requests
import sys


class Client(QDialog):
    def __init__(self):
        super().__init__()
        self.host = "http://localhost:8000/"
        print("Client was created")

    def getRequest(self):
        req = requests.get(self.host + "/get-data")
        print(req.headers)
        print(req.text)

    def postRequest(self, new_data):
        hdrs = {'Content-type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        req = requests.post(self.host + "/post-data", data=new_data, headers=hdrs)
        print(req.headers)
        print(req.text)


if __name__ == '__main__':
    data = {"name": "Soldatova Kira",
            "year": 2004,
            "course": 1,
            "group": 224}
    app = QApplication(sys.argv)
    client = Client()
    client.postRequest(data)
    client.getRequest()
    sys.exit(client.exec_())
