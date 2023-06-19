from PyQt5.QtCore import QDataStream, QIODevice
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket
import sys


class Client(QDialog):
    def __init__(self):
        super().__init__()
        self.tcpSocket = QTcpSocket(self)
        self.blockSize = 0
        self.makeRequest()
        self.tcpSocket.waitForConnected(1000)
        self.tcpSocket.write(b'hello from client')
        self.tcpSocket.readyRead.connect(self.dealCommunication)
        self.tcpSocket.error.connect(self.displayError)

    def makeRequest(self):
        host = '127.0.0.1'
        port = 8000
        self.tcpSocket.connectToHost(host, port, QIODevice.ReadWrite)

    def dealCommunication(self):
        received_data = QDataStream(self.tcpSocket)
        received_data.setVersion(QDataStream.Qt_5_0)
        if self.blockSize == 0:
            if self.tcpSocket.bytesAvailable() < 2:
                return
            self.blockSize = received_data.readUInt16()
        if self.tcpSocket.bytesAvailable() < self.blockSize:
            return
        # Print response to terminal, we could use it anywhere else we wanted.
        print(str(received_data.readString(), encoding='ascii'))

    def displayError(self, socketError):
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        else:
            print(self, "The following error occurred: %s." % self.tcpSocket.errorString())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    sys.exit(client.exec_())
