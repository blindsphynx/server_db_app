from PyQt5.QtCore import QDataStream, QIODevice
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket


class Client:
    def __init__(self):
        self.tcpSocket = QTcpSocket()
        self.blockSize = 0
        # self.tcpSocket.error.connect(self.displayError)
        print("Client was created")

    def makeRequest(self):
        host = '127.0.0.1'
        port = 8000
        self.tcpSocket.connectToHost(host, port, QIODevice.ReadWrite)
        if self.tcpSocket.waitForConnected(1000):
            self.tcpSocket.write(b'hello from client')
            self.tcpSocket.readyRead.connect(self.dealCommunication)
            print("message sent!")

    def dealCommunication(self):
        received_data = QDataStream(self.tcpSocket)
        received_data.setVersion(QDataStream.Qt_5_0)
        if self.blockSize == 0:
            if self.tcpSocket.bytesAvailable() < 2:
                return
            self.blockSize = received_data.readUInt16()
        if self.tcpSocket.bytesAvailable() < self.blockSize:
            return
        print(str(received_data.readString(), encoding='ascii'))

    def displayError(self, socketError):
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        else:
            print(self, "The following error occurred: %s." % self.tcpSocket.errorString())


if __name__ == '__main__':
    client = Client()
    client.makeRequest()
