import json
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QDataStream, QIODevice, QUrl, QByteArray
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QLineEdit, QWidget, QMessageBox, QPushButton, \
    QInputDialog
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket, QNetworkRequest, QNetworkAccessManager
import sys


class Client(QDialog):
    def __init__(self):
        super().__init__()
        self.tcpSocket = QTcpSocket(self)
        self.blockSize = 0
        print("Client was created")
        self.makeRequest()
        if self.tcpSocket.waitForConnected():
            print("Connected to the host")
            self.sendMessage()
            self.tcpSocket.readyRead.connect(self.dealCommunication)
            self.tcpSocket.error.connect(self.displayError)
        else:
            print("Cannot connect to the host")

    def makeRequest(self):
        host = '127.0.0.1'
        port = 8000
        self.tcpSocket.connectToHost(host, port, QIODevice.ReadWrite)

    def dealCommunication(self):
        if self.blockSize == 0:
            # print("Received bytes: ", self.tcpSocket.bytesAvailable())
            if self.tcpSocket.bytesAvailable() < 2:
                return
            self.blockSize = self.tcpSocket.bytesAvailable()
        if self.tcpSocket.bytesAvailable() < self.blockSize:
            return
        print(str(self.tcpSocket.read(100), encoding='ascii'))

    def sendMessage(self):
        self.tcpSocket.write(b'hello from client')
        # print("message sent!")

    def displayError(self, socketError):
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        else:
            print(self, "The following error occurred: %s." % self.tcpSocket.errorString())


def postRequest(self):
    self.url = QUrl()
    self.req = QWebEngineHttpRequest()

    self.url.setScheme("http")
    self.url.setHost("stackoverflow")
    self.url.setPath("/something/somethingelse")

    self.req.setUrl(self.url)
    self.req.setMethod(QWebEngineHttpRequest.Post)
    self.req.setHeader(QByteArray(b'Content-Type'), QByteArray(b'application/json'))

    params = {"something": value, "test": True, "number": 5}

    self.req.setPostData(bytes(json.dumps(params), 'utf-8'))

    return self.req


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()


    sys.exit(client.exec_())
